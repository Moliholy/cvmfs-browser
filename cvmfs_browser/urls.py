"""Cloud browser URLs."""
from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

from cvmfs_browser.app_settings import settings

# pylint: disable=invalid-name
urlpatterns = patterns(
    'cvmfs_browser.views',
    url(r'^browser/(?P<repo_name>[a-z\.\-]+)/$',
        'browser', name="cloud_browser_browser"),
    url(r'^browser/(?P<repo_name>[a-z\.\-]+)/(?P<revision>[^\/]*)/(?P<path>.*)$',
        'browser', name="cloud_browser_browser"),
    url(r'^document/(?P<repo_name>[a-z\.\-]+)/$',
        'document', name="cloud_browser_document"),
    url(r'^document/(?P<repo_name>[a-z\.\-]+)/(?P<revision>[^\/]*)/(?P<path>.*)$',
        'document', name="cloud_browser_document"),
)
