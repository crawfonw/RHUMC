"""
    Conference scheduling software for undergraduate institutions.
    Created specifically for the Mathematics department of the
    Rose-Hulman Institute of Technology (http://www.rose-hulman.edu/math.aspx).
    
    Copyright (C) 2013-2014  Nick Crawford <crawfonw -at- gmail.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

from subprocess import PIPE, Popen
from unicodedata import normalize

import os
import re
import tempfile
import zipfile

LATEX_REGEX = r'((?<!\\)[#\$%\^&_\{\}~])'
LATEX_RESERVED = {
    '&':  r'\&',
    '%':  r'\%', 
    '$':  r'\$', 
    '#':  r'\#', 
    '_':  r'\_', 
    '{':  r'\{', 
    '}':  r'\}',
    '~':  r'\textasciitilde{}', 
    '^':  r'\^{}', 
    '\\': r'\textbackslash{}',
}

#http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ['PATH'].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None

def str_to_file(s, file_name, file_ext):
    tempfile_d, tempfile_path = tempfile.mkstemp(prefix=file_name, suffix=file_ext if file_ext.startswith('.') else '.' + file_ext)
    f = open(tempfile_path, 'w')
    f.write(s)
    f.close()
    return (tempfile_d, tempfile_path,)
    
def compile_latex_to_pdf(tex, file_name):
    tempdir = tempfile.mkdtemp() + os.sep
    tempfile_d, tempfile_path = tempfile.mkstemp(prefix=file_name, suffix='.pdf', dir=tempdir)
    tempfile_ = os.path.split(tempfile_path)[1]
    filename = os.path.splitext(tempfile_)[0]

    #Need to call pdflatex twice to build ToC
    for i in range(2):
        process = Popen(['pdflatex', '-output-directory', tempdir, '-jobname', filename], stdin=PIPE, stdout=PIPE)
        process.communicate(tex)
        
    return (tempfile_d, tempfile_path,)

def zip_files_together(files, file_name):
    tempfile_d, tempfile_path = tempfile.mkstemp(prefix=file_name, suffix='.zip')
    with zipfile.ZipFile(tempfile_path, 'w') as zip:
        for f in files:
            zip.write(f, arcname=(file_name + '.' + os.path.basename(f).split('.')[1]))
    return (tempfile_d, tempfile_path,)

def clean_unicode_for_dict(model_dict):
    for key,val in model_dict.items():
        if isinstance(val, unicode):
            model_dict[key] = convert_unicode(val)
    return model_dict

def convert_unicode(unicode_string):
    return normalize('NFKD', unicode_string).encode('ascii', 'ignore') #use 'replace' for ?s instead of omitting

def escape_latex_for_dict(model_dict):
    for key,val in model_dict.items():
        if isinstance(val, unicode) or isinstance(val, str):
            model_dict[key] = escape_latex(val)
    return model_dict

def escape_latex(s):
    return re.sub(LATEX_REGEX, lambda m: ''.join('%s' % LATEX_RESERVED[i] for i in m.groups()), s)

