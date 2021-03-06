"""Cloud browser URLs."""
from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

from cvmfs_browser.app_settings import settings

# pylint: disable=invalid-name
urlpatterns = patterns(
    'cvmfs_browser.views',
    url(r'^browser/(?P<repo_name>[a-z\.\-0-9]+)/$',
        'browser', name="cloud_browser_browser"),
    url(r'^browser/(?P<repo_name>[a-z\.\-0-9]+)/(?P<revision>[^\/]*)/(?P<path>.*)$',
        'browser', name="cloud_browser_browser"),
    url(r'^document/(?P<repo_name>[a-z\.\-0-9]+)/$',
        'document', name="cloud_browser_document"),
    url(r'^document/(?P<repo_name>[a-z\.\-0-9]+)/(?P<revision>[^\/]*)/(?P<path>.*)$',
        'document', name="cloud_browser_document"),
    url(r'^diff/(?P<repo_name>[a-z\.\-0-9]+)/(?P<revision1>[^\/]*)/(?P<revision2>[^\/]*)/(?P<path>.*)$',
        'diff', name="cloud_browser_diff"),
)
