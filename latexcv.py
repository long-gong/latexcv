#!/usr/bin/env python3
from __future__ import print_function

import argparse
import os
import shlex
import sys

import six
from jinja2 import Environment, FileSystemLoader
from yaml import load
from utility import ExternalCommandWrapper, \
    FileRemoveWrapper, FileCopyWrapper, FileFilter, MakeDirWrapper, FileCopyError
from copy import deepcopy


class LaTEXCVMakerError(Exception):
    pass


def is_certain_file(f, f_ext):
    assert isinstance(f, six.string_types)
    return f.endswith(f_ext)


def is_tex_file(f):
    return is_certain_file(f, '.tex')


def is_pdf_file(f):
    return is_certain_file(f, '.pdf')


def is_cls_file(f):
    return is_certain_file(f, '.cls')


def is_tex_temp_files(f):
    temp_files_exts = {".blg", ".bbl", ".aux", ".log", ".brf", ".nlo", ".out", ".dvi", ".ps", ".lof", ".toc", ".fls",
                       ".fdb_latexmk", ".pdfsync", ".synctex.gz", ".ind", ".ilg", ".idx"}
    ext = os.path.splitext(f)[-1]
    return ext in temp_files_exts


def split_filename(filename_or_path):
    if filename_or_path.find('/') == -1:
        return filename_or_path, None
    else:
        if not os.path.isabs(filename_or_path):
            filename_or_path = os.path.abspath(filename_or_path)
        filename = os.path.basename(filename_or_path)
        path = os.path.dirname(filename_or_path)
        return filename, path


_ST3_BUILD_VARS_MAP = {
    '$file': '{file}',
    '$file_path': '{file_path}',
    '$file_base_name': '{file_base_name}',
    '$file_extension': '{file_extension}'

}


class LaTeXCVMaker:
    """A simple class for making CV."""

    def __init__(self, temp_dir='templates/default',
                 temp_files=('cv_multi.tex', 'cv_single.tex'),
                 tex_files=None,
                 cv_config='_config.yaml',
                 build_dir='build',
                 data_dir='bib',
                 lib_dir='includes',
                 tool_dir='tools',
                 only_tex=False,
                 delete_temp=True,
                 verbose=False,
                 **kwargs):
        self.temp_dir = temp_dir
        self.temp_files = temp_files
        self.tex_files = tex_files
        self.config_file = cv_config
        self.build_dir = build_dir
        self.data_dir = os.path.join(self.temp_dir, data_dir).replace('\\', '/')
        self.lib_dir = os.path.join(self.temp_dir, lib_dir).replace('\\', '/')
        self.tool_dir = tool_dir
        self.only_tex = only_tex
        self.delete_temp = delete_temp
        self.verbose = verbose
        self.kwargs = kwargs

        self.build_cmds = []

    def __process_b

    def __do_preparations(self):
        # make build directory a absolute path
        if not os.path.isabs(self.temp_dir):
            self.temp_dir = os.path.abspath(self.temp_dir)
        assert os.path.isdir(self.temp_dir)

        # process template filename(s) and tex filename(s) to make sure they do not contain paths
        if isinstance(self.temp_files, list) or isinstance(self.temp_files, tuple):
            assert (isinstance(self.tex_files, list) or isinstance(self.tex_files, tuple)) and \
                   len(self.tex_files) == len(self.temp_files)
            filenames = []
            for temp_file in self.temp_files:
                fname, path = split_filename(temp_file)
                assert (path is None) or (path == self.temp_dir)
                filenames.append(fname)
            self.temp_files = deepcopy(filenames)
            if not (self.tex_files is None):
                filenames = []
                for tex_file in self.tex_files:
                    fname, path = split_filename(tex_file)
                    assert (path is None) or (path == self.build_dir)
                    filenames.append(fname)
                self.tex_files = deepcopy(filenames)
        else:
            assert isinstance(self.temp_files, six.string_types)
            self.temp_files, path = split_filename(self.temp_files)
            assert (path is None) or (path == self.temp_dir)
            if isinstance(self.tex_files, six.string_types):
                self.tex_files, path = split_filename(self.tex_files)
                assert (path is None) or (path == self.build_dir)
        if self.tex_files is None:
            self.tex_files = deepcopy(self.temp_files)

        # process build directory
        #   step 1: check whether build directory exists or not, if not, create it
        if not os.path.isabs(self.build_dir):
            self.build_dir = os.path.abspath(self.build_dir)
        if not os.path.exists(self.build_dir):
            mkdir = MakeDirWrapper(verbose=self.verbose)
            mkdir.mkdir(self.build_dir)
        else:
            assert os.path.isdir(self.build_dir)
        #   step 2: copy dependencies to build directory
        try:
            cp = FileCopyWrapper(verbose=self.verbose)
            if self.data_dir is not None:
                if not os.path.isabs(self.data_dir):
                    self.data_dir = os.path.abspath(self.data_dir)
                cp.copy(self.data_dir, self.build_dir)
            if self.lib_dir is not None:
                if not os.path.isabs(self.lib_dir):
                    self.lib_dir = os.path.abspath(self.lib_dir)
                cp.copy(self.lib_dir, self.build_dir)
        except FileCopyError as e:
            print("Failed to copy dependent files: " + str(e))
            print("We assume that you have already copied tem manually")

        # prepare build commands
        if 'build_cmd' in self.kwargs:
            self.build_cmds.append(shlex.split(self.kwargs['build_cmd']))
        else:
            if self.verbose:
                print("Since you did not provide custom build command, the default one will be used!")
            if not os.path.isabs(self.tool_dir):
                self.tool_dir = os.path.abspath(self.tool_dir)
            if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
                if self.verbose:
                    print("You are using unix-based OS, we will try to use texliveonfly script to automatically "
                          "download LaTeX dependencies.")
                command = ['python3', '"{0}{1}texliveonfly.py"'.format(self.tool_dir, os.sep)]
                self.build_cmds.append(command)
            tex_build_command = shlex.split(
                'python3 "{tool_dir}{sep}latexrun{sep}latexrun"'.format(tool_dir=self.tool_dir, sep=os.sep))
            self.build_cmds.append(tex_build_command)

    def make_tex(self):
        """Generate tex code"""
        self.__do_preparations()
        try:
            temp_dir = [self.temp_dir]
            for f in os.listdir(self.temp_dir):
                if f.startswith('.'):
                    continue
                full_name = os.path.join(self.temp_dir, f).replace('\\', '/')
                if os.path.isdir(full_name):
                    temp_dir.append(full_name)
            if self.verbose:
                print("Adding `{0}` to jinja2's template file system".format(";".join(temp_dir)))
            j2_env = Environment(loader=FileSystemLoader(temp_dir),
                                 trim_blocks=True)
            config = load(open(self.config_file, 'r'))

            if isinstance(self.temp_files, list) or isinstance(self.temp_files, tuple):
                for temp_file, tex_file in zip(self.temp_files, self.tex_files):
                    tex_source = j2_env.get_template(temp_file).render({'cv': config})
                    self.__make_tex_file(tex_file, tex_source)
            else:
                assert isinstance(self.temp_files, six.string_types)
                tex_source = j2_env.get_template(self.temp_files).render({'cv': config})
                self.__make_tex_file(self.tex_files, tex_source)
        except OSError as e:
            raise LaTEXCVMakerError("Failed to make cv: " + str(e))

    def __make_tex_file(self, filename, tex_source):
        add_msg = "%% This file is generated by Jinja2"

        filename = os.path.join(self.build_dir, filename).replace('\\', '/')
        try:
            with open(filename, 'w') as texf:
                texf.write("%s\n" % add_msg)
                texf.write(tex_source)
        except OSError as e:
            raise LaTEXCVMakerError("Failed to create tex file `{0}`: ".format(filename) + str(e))

    def __make_pdf(self):
        ff = FileFilter(category='inclusive', verbose=self.verbose)
        for file in ff.filter(os.listdir(self.build_dir), [is_tex_file]):
            self.__make_single_pdf(file)

    def __make_single_pdf(self, tex_file):
        tex_file = os.path.join(self.build_dir, tex_file).replace('\\', '/')
        if self.verbose:
            print("Compiling `{0}`".format(tex_file))
        for cmd in self.build_cmds:
            cmd_ = ExternalCommandWrapper(cmd=cmd[0], cmd_args=cmd[1:] + [tex_file], cwd=self.build_dir,
                                          verbose=self.verbose)
            cmd_.run()

    def make_all(self):
        self.make_tex()
        self.__make_pdf()
        if self.delete_temp:
            self.__delete_temporary()

    def make(self):
        self.make_all()

    def __delete_temporary(self):
        ff = FileFilter(category='inclusive', verbose=self.verbose)
        rm = FileRemoveWrapper(verbose=self.verbose)
        rm_files = [os.path.join(self.build_dir, f).replace('\\', '/') for f in ff.filter(os.listdir(self.build_dir),
                                                                                          [is_tex_temp_files])]
        rm.remove(rm_files)


def arg_parser_shlex(s):
    """Argument parser for shell token lists.

       Shamelessly "copy" from https://github.com/aclements/latexrun
    """
    try:
        return shlex.split(s)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e))


def main():
    # Parse the command line
    arg_parser = argparse.ArgumentParser(
        description='''A simple LaTeX CV maker,
        `python3 %(prog)s` generates a LaTeX formatted CV based on the LaTeX template (you can 
        create your customized template or just use the built-in template) and then compiles the 
        LaTeX to make CV(s) in PDF(s) based on the compiling commands you provided (if you do not 
        provide any LaTeX compiling commands, it will use the built-in commands). \n\nEnjoy LaTeXCV.''')

    arg_parser.add_argument(
        '--temp-dir', metavar='DIR', dest='temp_dir', default='templates/default',
        help='Template directory (default: `templates/default`)')
    arg_parser.add_argument(
        '--temp-file', nargs='*', metavar='FILE', default=('cv_multi.tex', 'cv_single.tex'),
        dest='temp_files', help='template file(s) (default: `(cv_multi.tex, cv_single.tex)`)')
    arg_parser.add_argument(
        '--tex-file', nargs='*', metavar='FILE', dest='tex_files', help='.tex file(s) to be generated')
    arg_parser.add_argument(
        '--config-file', metavar='FILE', dest='config_file', default='_config.yaml',
        help='Configuration file formatted in YAML (default: `_config.yml`')
    arg_parser.add_argument(
        '--build-dir', metavar='DIR', dest='build_dir', default='build',
        help='Directory to generate your tex file(s) and compile (default: `build`)')
    arg_parser.add_argument(
        '--data-dir', metavar='DIR', dest='data_dir', default='bib',
        help='Directory where, for example, the bib file is stored (default: `bib`)')
    arg_parser.add_argument(
        '--lib-dir', metavar='DIR', dest='lib_dir', default='includes',
        help='Directory where to store customized LaTeX macros or customized class files '
             '(default: includes)')
    arg_parser.add_argument(
        '--tool-dir', metavar='DIR', dest='tool_dir', default='tools',
        help='Directory to store customized LaTeX compiling scripts (default: `tools`)')
    arg_parser.add_argument(
        '--not-delete-temp', action='store_true', dest='not_delete_temp', help='Not to delete temporary file(s).')
    arg_parser.add_argument(
        '--build-cmds', metavar='ARGS', type=arg_parser_shlex, nargs='*', dest='build_cmds',
        help='Custom LaTeX build commands, which will be parsed and split using POSIX shell rules. '
             '(We are trying to mimic the build systems of sublime text 3, but currently we only support '
             'very few features of it. More details can be found in README.md.)'
    )
    arg_parser.add_argument(
        '--only-tex', action='store_true', dest='only_tex', help='Only to generate tex (not to compile to PDF(s))'
    )
    arg_parser.add_argument(
        '-v', action='store_true', dest='verbose', help='Show verbose information.')

    args = arg_parser.parse_args()
    delete_temp = not args.not_delete_temp

    cv_maker = LaTeXCVMaker(
        temp_dir=args.temp_dir, temp_files=args.temp_files, tex_files=args.tex_files,
        cv_config=args.config_file, build_dir=args.build_dir, data_dir=args.data_dir,
        lib_dir=args.lib_dir, tool_dir=args.tool_dir, delete_temp=delete_temp,
        only_tex=args.only_tex, verbose=args.verbose, build_cmds=args.build_cmds
    )
    cv_maker.make()


if __name__ == '__main__':
    main()

