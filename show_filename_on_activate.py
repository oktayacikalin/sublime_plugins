'''
Shows current filename in status bar when the view gets activated.

@author: Oktay Acikalin <ok@ryotic.de>

@license: MIT (http://www.opensource.org/licenses/mit-license.php)

@since: 2011-02-28
'''

import sublime
import sublime_plugin


class ShowFilenameOnActivateListener(sublime_plugin.EventListener):

    def on_activated(self, view):
        filename = view.file_name() or view.name()
        sublime.status_message('Current view: %s' % filename)
