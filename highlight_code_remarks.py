'''
Event listener which scans content, finds special remark words like FIXME,
TODO, WARNING, INFO or DONE and highlights them.

You might want to override the following parameters within your file settings:
* highlight_code_remarks_max_file_size
  Restrict this to a sane size in order not to DDOS your editor.

Add these to your theme (and optionally adapt the colors to your liking):
        <dict>
            <key>name</key>
            <string>Remark TODO</string>
            <key>scope</key>
            <string>remark.todo</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>#FFFFAA</string>
            </dict>
        </dict>
        <dict>
            <key>name</key>
            <string>Remark DONE</string>
            <key>scope</key>
            <string>remark.done</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>#AAFFAA</string>
            </dict>
        </dict>
        <dict>
            <key>name</key>
            <string>Remark WAIT</string>
            <key>scope</key>
            <string>remark.wait</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>#FFFFAA55</string>
            </dict>
        </dict>
        <dict>
            <key>name</key>
            <string>Remark NOTE</string>
            <key>scope</key>
            <string>remark.note</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>#AAAAAA</string>
            </dict>
        </dict>
        <dict>
            <key>name</key>
            <string>Remark FIXME</string>
            <key>scope</key>
            <string>remark.fixme</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>#FFAAAA</string>
            </dict>
        </dict>
        <dict>
            <key>name</key>
            <string>Remark WARNING</string>
            <key>scope</key>
            <string>remark.warning</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>#FB9A4B</string>
            </dict>
        </dict>
        <dict>
            <key>name</key>
            <string>Remark INFO</string>
            <key>scope</key>
            <string>remark.info</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>#FFFFAA</string>
            </dict>
        </dict>
        <dict>
            <key>name</key>
            <string>Remark EXCEPTION</string>
            <key>scope</key>
            <string>remark.exception</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>#FFAAAA</string>
            </dict>
        </dict>
        <dict>
            <key>name</key>
            <string>Remark ERROR</string>
            <key>scope</key>
            <string>remark.error</string>
            <key>settings</key>
            <dict>
                <key>foreground</key>
                <string>#FB9A4B</string>
            </dict>
        </dict>

@author: Oktay Acikalin <ok@ryotic.de>

@license: MIT (http://www.opensource.org/licenses/mit-license.php)

@since: 2011-02-26
'''

import sublime

from support.view import DeferedViewListener


DEFAULT_MAX_FILE_SIZE = 1048576

REMARK_COLORS = {
    'TODO': 'remark.todo',
    'DONE': 'remark.done',
    'WAIT': 'remark.wait',
    'NOTE': 'remark.note',
    'FIXME': 'remark.fixme',
    'WARNING': 'remark.warning',
    'INFO': 'remark.info',
    'EXCEPTION': 'remark.exception',
    'ERROR': 'remark.error',
}


class HighlightCodeRemarksListener(DeferedViewListener):

    def __init__(self):
        super(HighlightCodeRemarksListener, self).__init__()
        color_keys, color_values = zip(*REMARK_COLORS.items())
        # print color_keys
        # print color_values
        pattern = r'(?:^[ \t]*?[*]+[ \t]*)?\<(%s)\>(?:[^\'\"\n\[\]\!\?]+?[:])?'
        regex = pattern % '|'.join(color_keys)
        regex = '(?:' + regex + ')'
        # print 'regex =', regex
        self.regex = regex
        self.color_keys = color_keys
        self.color_values = color_values
        self.max_size_setting = 'highlight_code_remarks_max_file_size'
        self.default_max_file_size = DEFAULT_MAX_FILE_SIZE
        self.delay = 500

    def view_is_too_big_callback(self, view):
        for color_value in self.color_values:
            tag = 'HighlightCodeRemarksListener.%s' % color_value
            view.erase_regions(tag)

    def update(self, view):
        remarks = []
        regions = view.find_all(self.regex, sublime.OP_REGEX_MATCH,
                                '$0', remarks)
        results = dict()
        for pos, region in enumerate(regions):
            remark = remarks[pos]
            remark = remark.strip('\t :*')
            # print pos, region, remark
            color_value = False
            for key, val in REMARK_COLORS.iteritems():
                # print key, val, remark
                if remark.startswith(key):
                    color_value = val
                    break
            if not color_value:
                continue
            # print color_value
            if color_value not in results:
                results[color_value] = list()
            results[color_value].append(region)
        # print results
        for color_value in self.color_values:
            tag = 'HighlightCodeRemarksListener.%s' % color_value
            if color_value in results:
                # print 'add', tag, results[color_value], color_value
                view.add_regions(tag, results[color_value], color_value,
                                 sublime.DRAW_EMPTY)
            else:
                # print 'remove', tag
                view.erase_regions(tag)
