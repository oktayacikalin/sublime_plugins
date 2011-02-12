'''
Highlights trailing spaces.

You might want to override the following parameters within your file settings:
* highlight_trailing_spaces_max_file_size
  Restrict this to a sane size in order not to DDOS your editor.
* highlight_trailing_spaces_color_name
  Change this to a valid scope name, which has to be defined within your theme.

@author: Oktay Acikalin <ok@ryotic.de>

@license: MIT (http://www.opensource.org/licenses/mit-license.php)

@since: 2011-02-11
'''

import sublime
import sublime_plugin


DEFAULT_MAX_FILE_SIZE = 1048576
DEFAULT_COLOR_NAME = 'comment'


class HighlightTrailingSpacesListener(sublime_plugin.EventListener):
    '''
    An event listener to highlight trailing spaces.
    '''

    def highlight(self, view):
        '''
        Searches for trailing spaces and highlights them.

        @type  view: sublime.View
        @param view: View to work with.

        @return: None
        '''
        settings = view.settings()

        max_size = settings.get('highlight_trailing_spaces_max_file_size',
                                DEFAULT_MAX_FILE_SIZE)
        if max_size not in (None, False):
            max_size = long(max_size)
            cur_size = view.size()
            if cur_size > max_size:
                view.erase_regions('HighlightTrailingSpacesListener')
                return
        
        color_name = settings.get('highlight_trailing_spaces_color_name',
                                  DEFAULT_COLOR_NAME)
        trails = view.find_all('([ \t]+)$')
        regions = []
        for trail in trails:
            regions.append(trail)
        view.add_regions('HighlightTrailingSpacesListener', regions, color_name,
                         sublime.DRAW_EMPTY_AS_OVERWRITE)

    def on_load(self, view):
        '''
        Event callback to react on loading of the document.

        @type  view: sublime.View
        @param view: View to work with.

        @return: None
        '''
        self.highlight(view)

    def on_activated(self, view):
        '''
        Event callback to react on activation of the document.

        @type  view: sublime.View
        @param view: View to work with.

        @return: None
        '''
        self.highlight(view)

    def on_modified(self, view):
        '''
        Event callback to react on modification of the document.

        @type  view: sublime.View
        @param view: View to work with.

        @return: None
        '''
        self.highlight(view)
