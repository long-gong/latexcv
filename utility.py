from __future__ import print_function
import errno
import os
import shutil
import subprocess
import six
from send2trash import send2trash


class ExternalCommandError(Exception):
    pass


class ExternalCommandWrapper:
    """A simple wrapper for executing all kinds of external commands, e.g., ls"""

    def __init__(self, cmd, cmd_args=None, shell=False, cwd=None, verbose=False):
        if cmd_args is None:
            cmd_args = []
        self.cmd = cmd
        self.cmd_args = cmd_args
        self.shell = shell
        self.cwd = cwd
        self.verbose = verbose

    def run(self):
        """Run the command"""
        full_cmd = [self.cmd]
        if len(self.cmd_args) > 0:
            full_cmd += self.cmd_args
        try:
            if self.verbose:
                print("Running `{command}`".format(command=" ".join(full_cmd)))
            p = subprocess.Popen(full_cmd,
                                 shell=self.shell,
                                 cwd=self.cwd,
                                 stdin=subprocess.DEVNULL,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
            p.wait()
            p.stdout.close()
        except OSError as e:
            raise ExternalCommandError("Failed to execute command: " + str(e))


class FileCopyError(Exception):
    pass


def copy_wrapper(src, dst, symlinks=False, ignore=None):
    """This function provides a wrapper to copy APIs in `shutil` to
       mimic the behaviors of `cp` in `bash`.

       For example, if `src` is a directory, and `dst` is also a directory and it
       exists, then this function creates a fold named `src` (by removing its parents)
       and copy all files in `src` to `dst/src`.

    """
    if os.path.exists(dst) and os.path.isdir(dst):
        if os.path.isdir(src):
            copy_dir = os.path.basename(src)
            dst = os.path.join(dst, copy_dir).replace('\\', '/')
            shutil.copytree(src, dst, symlinks, ignore)
        else:
            copy_file = os.path.basename(src)
            dst = os.path.join(dst, copy_file).replace('\\', '/')
            shutil.copy2(src, dst)
    else:
        try:
            shutil.copytree(src, dst)
        except OSError as e:
            if e.errno == errno.ENOTDIR:
                shutil.copy(src, dst)
            else:
                raise FileCopyError("Failed to copy `{0}` to `{1}`: ".format(src, dst) + str(e))


class FileCopyWrapper:
    """A simple wrapper class for coping file(s) or directories"""

    def __init__(self, verbose=False):
        self.verbose = verbose

    def copy(self, src, dst):
        """Copy all files/directories in src to dst.
        Note that
            - `src` can be a str for a file or a directory, or a list/tuple for
               a set of files/directories. However, `dst` can only be a str for a file or a directory.
            - If `str` is a list/tuple of strings, then `dst` MUST be a name for directory.
            - This function does not check whether the `dst` file exists or not, or the `dst` directory
              is empty or not.
        """
        if isinstance(src, six.string_types):
            self.__copy(src, dst)
        else:
            assert isinstance(src, list) or isinstance(src, tuple)
            for src_file in src:
                assert isinstance(src_file, six.string_types)
                self.__copy(src_file, dst)

    def __copy(self, src, dst):
        """Copy src to dst
        Source: https://stackoverflow.com/questions/1994488/copy-file-or-directories-recursively-in-python
        """
        if self.verbose:
            print("Copying from `{0}` to '{1}`".format(src, dst))
        try:
            copy_wrapper(src, dst)
        except OSError as e:
            raise FileCopyError("Failed to copy `{0}` to `{1}`: ".format(src, dst) + str(e))


class MakeDirError(Exception):
    pass


class MakeDirWrapper:
    """Simple wrapper for `os.mkdirs`"""

    def __init__(self, verbose=False):
        self.verbose = verbose

    def mkdir(self, directories):
        """Create directories"""
        if isinstance(directories, six.string_types):
            self.__mkdir(directories)
        else:
            assert isinstance(directories, list) or isinstance(directories, tuple)
            for directory in directories:
                assert isinstance(directory, six.string_types)
                self.__mkdir(directory)

    def __mkdir(self, path):
        """Create directories"""
        if self.verbose:
            print("Create `{}`".format(path))
        try:
            os.stat(path)
            if self.verbose:
                print("[WARNING]: `{}` already exists".format(path))
        except:
            try:
                os.makedirs(path)
            except OSError as e:
                raise MakeDirError("Failed to create `{}`:".format(path) + str(e))


class FileRemoveError(Exception):
    pass


class FileRemoveWrapper:
    """Simple wrapper for send2trash"""
    def __init__(self, verbose=False):
        self.verbose = verbose

    def remove(self, files, ignore=None):
        """Remove files"""
        if isinstance(files, six.string_types):
            if (ignore is None) or (not ignore(files)):
                self.__remove(files)
        else:
            assert isinstance(files, list) or isinstance(files, tuple)
            for file in files:
                assert isinstance(file, six.string_types)
                if (ignore is None) or (not ignore(file)):
                    self.__remove(file)

    def __remove(self, some_file_or_dir):
        """Send `some_file_or_dir` to trash"""
        if self.verbose:
            print("Removing `{0}`".format(some_file_or_dir))
        try:
            send2trash(some_file_or_dir)
        except OSError as e:
            raise FileRemoveError("Failed to remove `{}`: ".format(some_file_or_dir) + str(e))


class FileFilterError(Exception):
    pass


def filter_check(filters):
    for f in filters:
        assert callable(f)


class FileFilter:
    """A simple class for doing file filter.
    """
    def __init__(self, category='inclusive', verbose=False):
        assert category == 'inclusive' or category == 'exclusive'
        self.category = category
        self.verbose = verbose

    def filter(self, files, filters):
        filter_check(filters)
        if isinstance(files, six.string_types):
            if self.__pass(files, filters):
                return files
        else:
            assert isinstance(files, list) or isinstance(files, tuple)
            filtered_files = []
            for file in files:
                assert isinstance(file, six.string_types)
                if self.__pass(file, filters):
                    filtered_files.append(file)
            return filtered_files

    def __pass(self, file, filters):
        if self.verbose:
            print("Filtering `{0}`".format(file))
        inclusive = (self.category == 'inclusive')
        for f in filters:
            if inclusive:
                if not f(file):
                    return False
            else:
                if f(file):
                    return False
        if self.verbose:
            print("\t\t\t\t\t\t... passed")
        return True




