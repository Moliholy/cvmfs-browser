"""Cloud browser template tags."""
import os

from django import template
from django.template import TemplateSyntaxError, Node
from django.template.defaultfilters import stringfilter

from cvmfs_browser.app_settings import settings

register = template.Library()  # pylint: disable=C0103


@register.filter
@stringfilter
def truncatechars(value, num, end_text="..."):
    """Truncate string on character boundary.

    .. note::
        Django ticket `5025 <http://code.djangoproject.com/ticket/5025>`_ has a
        patch for a more extensible and robust truncate characters tag filter.

    Example::

        {{ my_variable|truncatechars:22 }}

    :param value: Value to truncate.
    :type  value: ``string``
    :param num: Number of characters to trim to.
    :type  num: ``int``
    """
    length = None
    try:
        length = int(num)
    except ValueError:
        pass

    if length is not None and len(value) > length:
        return value[:length-len(end_text)] + end_text

    return value
truncatechars.is_safe = True  # pylint: disable=W0612


@register.filter
@stringfilter
def increment_page(current_page):
    page_int = int(current_page) + 1
    return str(page_int)


@register.filter
@stringfilter
def decrement_page(current_page):
    page_int = int(current_page) - 1
    return str(page_int) if page_int >= 0 else '0'


@register.filter
@stringfilter
def make_page_parameter(page):
    return '?page=' + page


@register.tag
def cloud_browser_media_url(_, token):
    """Get base static URL for application static static.

    Correctly handles whether or not the settings variable
    ``CLOUD_BROWSER_STATIC_MEDIA_DIR`` is set and served.

    For example::

        <link rel="stylesheet" type="text/css"
            href="{% cloud_browser_media_url "css/cloud-browser.css" %}" />
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("'%s' takes one argument" % bits[0])
    rel_path = bits[1]

    return MediaUrlNode(rel_path)


@register.filter
@stringfilter
def get_file_name(string):
    return string.split('/')[-1]


class MediaUrlNode(Node):
    """Media URL node."""

    #: Static application static URL (or ``None``).
    static_media_url = settings.app_media_url

    def __init__(self, rel_path):
        """Initializer."""
        super(MediaUrlNode, self).__init__()
        self.rel_path = rel_path.lstrip('/').strip("'").strip('"')

    def render(self, context):
        """Render."""
        from django.core.urlresolvers import reverse

        # Check if we have real or Django static-served media
        if self.static_media_url is not None:
            # Real.
            return os.path.join(self.static_media_url, self.rel_path)

        else:
            # Django.
            return reverse("cloud_browser_media",
                           args=[self.rel_path],
                           current_app='cloud_browser')
