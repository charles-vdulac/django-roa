from django.conf import settings
from django.utils.html import strip_tags
from django.utils.text import unescape_entities
from django.utils.encoding import force_unicode

ROA_DJANGO_ERRORS = getattr(settings, 'ROA_DJANGO_ERRORS', False)

class ROAException(Exception):
    def __init__(self, exception):
        if ROA_DJANGO_ERRORS and 'message' in exception \
                             and 'status_code' in exception:
            self.msg = force_unicode(exception.message)
            self.status_code = exception.status_code
        else:
            self.msg = force_unicode(exception)
            self.status_code = 'XXX'

    def __str__(self):
        if ROA_DJANGO_ERRORS and '<body>' in self.msg:
            return self.parse_django_error()
        return self.msg

    def parse_django_error(self):
        """Extract the summary part of a Django HTML error."""
        try:
            summary = self.msg.split(u'<body>\n<div id="summary">\n  ', 1)[1]\
                              .split(u'<th>Python Executable:</th>', 1)[0]
            traceback = self.msg.split(u'\n\nTraceback:', 1)[1]\
                                .split(u'</textarea>', 1)[0]
        except IndexError:
            return self.msg
        result = []
        title = None
        for line in strip_tags(summary).split('\n'):
            line_content = unescape_entities(line.strip())
            if line_content:
                if line_content.endswith(':'):
                    title = line_content
                elif title is None:
                    title = "%s:" % line_content
                else:
                    result.append("%s %s\n" % (title, line_content))
        result.append("Status code: %s" % self.status_code)
        indent, indent2 = u'  ', u'    '
        return u"%(summary)s %(traceback)s".strip() % {
            'summary': indent.join(force_unicode(line) for line in result),
            'traceback': indent2.join(force_unicode(line+"\n") \
                                        for line in traceback.split('\n')),
        }


class ROANotImplementedYetException(Exception):
    pass
