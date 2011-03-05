'''
Stores syntax file from last activated view and reuses this for a new view.

@author: Oktay Acikalin <ok@ryotic.de>

@license: MIT (http://www.opensource.org/licenses/mit-license.php)

@since: 2011-03-05
'''

import sublime_plugin


class NewFileSyntaxListener(sublime_plugin.EventListener):

    def __init__(self, *args, **kwargs):
        super(NewFileSyntaxListener, self).__init__(*args, **kwargs)
        self.last_syntax = None

    def on_new(self, view):
        if self.last_syntax:
            view.set_syntax_file(self.last_syntax)

    def on_activated(self, view):
        self.last_syntax = view.settings().get('syntax')
