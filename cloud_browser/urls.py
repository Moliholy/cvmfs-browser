"""Cloud browser URLs."""
from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

from cloud_browser.app_settings import settings

# pylint: disable=invalid-name
urlpatterns = patterns(
    'cloud_browser.views',
    url(r'^browser/(?P<repo_name>[a-z\.\-]+)/$',
        'browser', name="cloud_browser_browser"),
    url(r'^browser/(?P<repo_name>[a-z\.\-]+)/(?P<revision>[^\/]*)/(?P<path>.*)$',
        'browser', name="cloud_browser_browser"),
    url(r'^document/(?P<repo_name>[a-z\.\-]+)/$',
        'document', name="cloud_browser_document"),
    url(r'^document/(?P<repo_name>[a-z\.\-]+)/(?P<revision>[^\/]*)/(?P<path>.*)$',
        'document', name="cloud_browser_document"),
)

if settings.app_media_url is None:
    # Use a static serve.
    urlpatterns += patterns(
        '',
        url(r'^app_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.app_media_doc_root},
            name="cloud_browser_media"),
    )
