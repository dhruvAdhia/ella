from widgets import RichTextAreaWidget

from django.newforms import fields
from django.newforms.util import ValidationError
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _

from ella.core.templatetags.core import render_str

import re

# FIXME: we have blank=True in models, but RichTextAreaField is still required!

class RichTextAreaField(fields.Field):
    widget = RichTextAreaWidget
    default_error_messages = {
        'syntax_error': _('Bad syntax in markdown formatting or template tags.'),
        'url_error':  _('Some links are invalid: %s.'),
        'link_error':  _('Some links are broken: %s.'),
}

    def __init__(self, *args, **kwargs):
        super(RichTextAreaField, self).__init__(*args, **kwargs)

    def _check_url(self, match):

        # FIXME: (?) I have problem testing development urls (future listngs) http://localhost:3000/...

        link = match.group(1)

        import urllib2
        headers = {
            "Accept": "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
            "Accept-Language": "en-us,en;q=0.5",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
            "Connection": "close",
            "User-Agent": fields.URL_VALIDATOR_USER_AGENT,
}

        try:
            req = urllib2.Request(link, None, headers)
            urllib2.urlopen(req)
        except ValueError:
            self.invalid_links.append(link)
        except:

            # try with GET parameter "ift=t" for our objects with future listing
            if '?' in link:
                tlink = link + '&ift=t'
            else:
                tlink = link + '?ift=t'

            try:
                req = urllib2.Request(tlink, None, headers)
                urllib2.urlopen(req)
            except:
                self.broken_links.append(link)

    def clean(self, value):
        "Validates markdown and temlate (box) syntax, validates links and check if exists."

        super(RichTextAreaField, self).clean(value)
        if value in fields.EMPTY_VALUES:
            return u''
        value = smart_unicode(value)

        # validate markdown links
        l = re.compile('\[.+\]\((.+)\)')
        self.invalid_links = []
        self.broken_links  = []
        l.sub(self._check_url, value)

        i = self.error_messages['url_error'] % ', '.join(self.invalid_links)
        b = self.error_messages['link_error'] % ', '.join(self.broken_links)
        if self.invalid_links and self.broken_links:
            raise ValidationError("%s %s" % (i, b))
        elif self.invalid_links:
            raise ValidationError(i)
        elif self.broken_links:
            raise ValidationError(b)

        # test render template
        try:
            render_str(value)
        except:
            raise ValidationError(self.error_messages['syntax_error'])

        return value