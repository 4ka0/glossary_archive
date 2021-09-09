import re
from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def highlight_query(text, query):
    highlighted = re.sub('(?i)(%s)' % (re.escape(query)),
                         '<span class="highlight_query">\\1</span>', text)
    return mark_safe(highlighted)
