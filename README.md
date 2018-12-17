# LaTeXCV: A LaTeX CV Maker

`LaTeXCV` is a simple tool to make personal resume in PDF (**NOT HTML**).  `LaTeX` is highly inspired by lots of websites build systems such as [Jekyll](https://jekyllrb.com/). The basic idea behind `LaTeXCV` is just to mimic the famous [MVC framework](https://www.tutorialspoint.com/mvc_framework/mvc_framework_introduction.htm). `LaTeXCV` decomposes the "view" (_e.g.,_ the layout and format) and "data" (_e.g.,_ texts of your experiences) of the resume. With `LaTeXCV`, you can:
+ Maintaining your CV by only maintaining a simple [YAML](https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html) file.
+ Updating how your resume should look by simply update a LaTeX template file without, for example, copying all your texts from a LaTeX file to another one.
+ Keeping multiple versions (_e.g.,_ a full version and a one-page version) without multiple copies of your texts. Otherwise, it might be troublesome to keep all texts consistent in different versions. 





## Getting Started

### Prerequisites

Although we did not conduct enough tests, this tool should work on Liunx, macOS and Windows.

+ Python (**Suggested to use Python 3.x**)
+ [TeX live](https://www.tug.org/texlive/) or [MiKTex](https://miktex.org/)

If you want to generate LaTeX documents with this tool, then you do not need [TeX live](https://www.tug.org/texlive/) or [MiKTex](https://miktex.org/).

### Download & Install Dependent Python Libraries

```bash
git clone https://github.com/long-gong/latexcv.git
cd latexcv
git submodule update --init --recursive
pip3 install --user -r requirements.txt
```

## Using `LaTeXCV`


### Usage Info & Examples

```shell
usage: latexcv.py [-h] [--temp-dir DIR] [--temp-file [FILE [FILE ...]]]
                  [--tex-file [FILE [FILE ...]]] [--config-file FILE]
                  [--build-dir DIR] [--data-dir DIR] [--lib-dir DIR]
                  [--tool-dir DIR] [--not-delete-temp]
                  [--build-cmds [ARGS [ARGS ...]]] [--only-tex] [-v]

A simple LaTeX CV maker, `python3 latexcv.py` generates a LaTeX formatted CV
based on the LaTeX template (you can create your customized template or just
use the built-in template) and then compiles the LaTeX to make CV(s) in PDF(s)
based on the compiling commands you provided (if you do not provide any LaTeX
compiling commands, it will use the built-in commands). Enjoy LaTeXCV.

optional arguments:
  -h, --help            show this help message and exit
  --temp-dir DIR        Template directory (default: `templates/default`)
  --temp-file [FILE [FILE ...]]
                        template file(s) (default: `(cv_multi.tex,
                        cv_single.tex)`)
  --tex-file [FILE [FILE ...]]
                        .tex file(s) to be generated
  --config-file FILE    Configuration file formatted in YAML (default:
                        `_config.yml`
  --build-dir DIR       Directory to generate your tex file(s) and compile
                        (default: `build`)
  --data-dir DIR        Directory where, for example, the bib file is stored
                        (default: `bib`)
  --lib-dir DIR         Directory where to store customized LaTeX macros or
                        customized class files (default: includes)
  --tool-dir DIR        Directory to store customized LaTeX compiling scripts
                        (default: `tools`)
  --not-delete-temp     Not to delete temporary file(s).
  --build-cmds [ARGS [ARGS ...]]
                        Custom LaTeX build commands, which will be parsed and
                        split using POSIX shell rules. (We are trying to mimic
                        the build systems of sublime text 3, but currently we
                        only support very few features of it. More details can
                        be found in README.md.)
  --only-tex            Only to generate tex (not to compile to PDF(s))
  -v                    Show verbose information.
```

For example,
```bash
python3 ./latexcv.py --tex-file long_full_2019.tex long_intern_2019.tex --build-dir build-test
```


### Build Systems

The built-in build system is [`latexrun`](https://github.com/aclements/latexrun) which is a Python wrapper for running various LaTeX build commands. To support On-the-fly downloading of missing TeX live packages on macOS and Linux, `LaTeXCV` first builds the LaTeX documents with [`texliveonfly`](https://ctan.org/pkg/texliveonfly?lang=en).

As mentioned in the usage of `LaTeXCV`, besides the built-in build system, `LaTeXCV` is trying to support custom LaTeX build systems. The syntax for writing the build system mimics that of [Sublime Text](https://www.sublimetext.com/). For example, you can use build commans like `pdflatex -synctex=1 -interaction=nonstopmode $file`. Currently, we only support the variable `$file`, and in the future we will add the supports for all necessary variables (Maybe still a subset of [build-system-variables](http://docs.sublimetext.info/en/latest/reference/build_systems/configuration.html#build-system-variables)).






