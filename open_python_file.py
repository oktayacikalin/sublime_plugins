'''
A text command to scan selections for Python imports, open the referenced files
and temporarily bookmark and highlight found symbols.

For use add something like this to your user definable key bindings file:
{ "keys": ["super+shift+o"], "command": "open_python_file" }

Configurable file settings:
* open_python_file_vrun_executable: Optional wrapper for e.g. virtualenv. E.g.:
  "open_python_file_vrun_executable": ["/users/oktay/code/bin/vrun.sh"]

@author: Oktay Acikalin <ok@ryotic.de>

@license: MIT (http://www.opensource.org/licenses/mit-license.php)

@since: 2011-02-20
'''

import os
import re
import subprocess

import sublime
import sublime_plugin

import find_python_imports


class Highlighter(object):
    '''
    Class which tries to highlight given symbols as soon as the file has been
    loaded.
    '''

    def __init__(self, view, symbols):
        '''
        Initializes the object.

        @type     view: sublime.View
        @param    view: View to work with.
        @type  symbols: list
        @param symbols: List with strings.

        @return: None
        '''
        self.view = view
        self.symbols = symbols
    
    def run(self):
        '''
        If view is loaded it tries to bookmark and select all symbols.
        If not it waits for 100ms and tries again.

        @return: None
        '''
        if self.view.is_loading():
            sublime.set_timeout(self.run, 100)
        else:
            regions = []
            for symbol in self.symbols:
                # print 'highlight:', symbol
                results = self.view.find_all('(def|class) %s(.*):' % symbol)
                results += self.view.find_all('%s\s*=.*' % symbol)
                if results:
                    regions += results
            if regions:
                regions = sorted(regions, key=lambda region: region.begin())
                # print regions
                self.view.add_regions('bookmarks', regions, 'bookmark',
                                      'bookmark', sublime.DRAW_OUTLINED)
                self.view.show_at_center(regions[0])
                sel = self.view.sel()
                sel.clear()
                sel.add(sublime.Region(regions[0].begin(), regions[0].begin()))


class OpenPythonFileCommand(sublime_plugin.TextCommand):
    '''
    A text command to scan selections for Python imports, open the referenced
    files and temporarily bookmark and highlight found symbols.
    '''

    begin_tag = 'xXxBEGINxXx>> '
    end_tag = ' <<xXxENDxXx'

    def get_import_file(self, module_ref, source_filename):
        '''
        Tries to load a Python file and query it's filepath.

        @type       module_ref: str
        @param      module_ref: A module path. E.g.: os.path
        @type  source_filename: str
        @param source_filename: Filepath of the caller.

        @rtype:  tuple(stdout, stderr)
        @return: Stdout with filepath and stderr with optional error messages.
        '''
        settings = sublime.load_settings('Global.sublime-settings')
        arg_list_wrapper = settings.get('open_python_file_vrun_executable')
        # Use vrun.sh to find matching Python file.
        vrun_cmd = 'cd "%s" && python -c "import os.path ; ' \
                   'import %s as module ; ' \
                   'print \'%s\' + os.path.abspath(module.__file__) ' \
                   '+ \'%s\'"' % (os.path.dirname(source_filename), module_ref,
                                  self.begin_tag, self.end_tag)
        cmd = [vrun_cmd]
        if arg_list_wrapper:
            cmd = arg_list_wrapper + [' '.join(cmd)]
            cmd += ['--origin', source_filename, '--quiet']
        # print 'cmd =', cmd
        stdout, stderr = subprocess.Popen(cmd,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          shell=not arg_list_wrapper,
                                          ).communicate()
        return stdout, stderr.strip()

    def load_module(self, module_ref, source_filename):
        '''
        Tries to load a Python file and returns the view.

        @type       module_ref: str
        @param      module_ref: A module path. E.g.: os.path
        @type  source_filename: str
        @param source_filename: Filepath of the caller.

        @rtype:  sublime.View
        @return: A view if the file could be openend, otherwise None.
        '''
        stdout, stderr = self.get_import_file(module_ref, source_filename)
        if stderr:
            regex = re.compile(r'\s*File "(?P<file>.+)", line \d+, in .*')
            matches = regex.findall(stderr)
            for match in matches:
                if os.path.isfile(match):
                    stdout, stderr = match, ''
                    break
        if stderr:
            print 'stdout =', stdout
            print 'stderr =', stderr
            sublime.error_message(stderr)
            return
        
        module_filename = stdout.strip()
        if module_filename.startswith(self.begin_tag):
            module_filename = module_filename[len(self.begin_tag):]
        if module_filename.endswith(self.end_tag):
            module_filename = module_filename[:-len(self.end_tag)]
        # print 'module_filename =', module_filename

        module_filename, module_ext = os.path.splitext(module_filename)
        if module_ext in ('.pyc', '.pyo'):
            module_ext = '.py'
        module_filename += module_ext
        # print 'module_filename =', module_filename

        return self.window.open_file(module_filename)

    def find_imports(self):
        '''
        Tries to find all imports in all selections and returns the results.

        @rtype:  list
        @return: A list with tuples each containing a module and symbols.
        '''
        module_refs = []
        for selection in self.view.sel():
            # print selection
            if selection.empty():
                selection = self.view.line(selection)
            content = self.view.substr(selection)
            imports = find_python_imports.parse(content)
            for ref_type, ref_module, ref_symbols in imports:
                module_refs.append((ref_module, ref_symbols))
        return module_refs

    def run(self, edit):
        '''
        Tries to find all imports, opens the files and highlights the results.

        @type  edit: sublime.Edit
        @param edit: Unused.

        @return: None
        '''
        self.window = self.view.window()
        source_filename = self.view.file_name()
        for module_ref, symbols in self.find_imports():
            view = self.load_module(module_ref, source_filename)
            if symbols is not None:
                highlighter = Highlighter(view, symbols)
                highlighter.run()
