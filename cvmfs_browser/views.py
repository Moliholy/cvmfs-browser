"""Cloud browser views."""
import os
import time
import datetime
import magic
import urllib
import re
import httpagentparser
import difflib
from django.http import HttpResponse, Http404,\
    HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.utils.importlib import import_module

from cvmfs_browser.app_settings import settings
from cvmfs_browser.cloud import get_connection, get_connection_cls, errors
from cvmfs_browser.common import path_parts, path_join, path_yield


MAX_LIMIT = get_connection_cls().cont_cls.max_list


def settings_view_decorator(function):
    """Insert decorator from settings, if any.

    .. note:: Decorator in ``CLOUD_BROWSER_VIEW_DECORATOR`` can be either a
        callable or a fully-qualified string path (the latter, which we'll
        lazy import).
    """

    dec = settings.CLOUD_BROWSER_VIEW_DECORATOR

    # Trade-up string to real decorator.
    if isinstance(dec, basestring):
        # Split into module and decorator strings.
        mod_str, _, dec_str = dec.rpartition('.')
        if not (mod_str and dec_str):
            raise ImportError("Unable to import module: %s" % mod_str)

        # Import and try to get decorator function.
        mod = import_module(mod_str)
        if not hasattr(mod, dec_str):
            raise ImportError("Unable to import decorator: %s" % dec)

        dec = getattr(mod, dec_str)

    if dec and callable(dec):
        return dec(function)

    return function


def _breadcrumbs(path):
    """Return breadcrumb dict from path."""

    full = None
    crumbs = []
    for part in path_yield(path):
        full = path_join(full, part) if full else part
        crumbs.append((full, part))

    return crumbs

def _date_str_to_timestamp(date_str):
    if date_str:
        return int(time
               .mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d")
               .timetuple()))


@settings_view_decorator
def browser(request, repo_name, revision='latest', path=''):
    """View files in a file path.

    :param request: The request.
    :param repo_name: fully qualified repository name.
    :param revision: revision number or 'latest'.
    :param path: Path to resource, including container as first part of path.
    :param template: Template to render.
    """

    # Inputs.
    path = urllib.unquote(path)
    path = '/' + path if not os.path.isabs(path) else path
    container_path, object_path = path_parts(path)
    incoming = request.POST or request.GET or {}
    page = incoming['page'] if 'page' in incoming else '0'
    revision_date_str = incoming['revision_date'] \
        if 'revision_date' in incoming else None
    compare_revision_number = incoming['compare_revision_number'] \
        if 'compare_revision_number' in incoming else None
    compare_revision_date = incoming['compare_revision_date'] \
        if 'compare_revision_date' in incoming else None
    file_name = incoming['compare_file'] \
        if 'compare_file' in incoming else None

    revision_tmstamp = _date_str_to_timestamp(revision_date_str)
    compare_revision_tmstamp = _date_str_to_timestamp(compare_revision_date)

    try:
        url = settings.CLOUD_BROWSER_CVMFS_URL_MAPPING[repo_name]
        params = {'url': url, 'revision': revision, 'date': revision_tmstamp}
        conn = get_connection(params)

        # check the GET parameters
        if compare_revision_date or compare_revision_number or revision_tmstamp:
            res = re.findall('.*/cb/[a-z]+/[^/]+/[^/]+/', request.path)[0]
            pos_revision = res[:-1].rfind('/')
            pos_repo = res[:pos_revision].rfind('/')
            pos_method = res[:pos_repo].rfind('/')
            new_url = ''
            if compare_revision_number:
                new_url = '/'.join(
                    [res[0:pos_method], 'diff', repo_name, revision,
                     compare_revision_number, path, file_name])
                return HttpResponseRedirect(new_url)
            elif compare_revision_date:
                params = {'url': url, 'revision': revision, 'date': compare_revision_tmstamp}
                conn = get_connection(params)
                new_url = '/'.join(
                    [res[0:pos_method], 'diff', repo_name, revision,
                     str(conn.revision), path, file_name])
            elif revision_tmstamp:
                new_url = '/'.join(
                    [res[0:pos_revision], str(conn.revision), path])

            return HttpResponseRedirect(new_url)

        # if there are no GET parameters we proceed normally
        url = settings.CLOUD_BROWSER_CVMFS_URL_MAPPING[repo_name]
        params = {'url': url, 'revision': revision, 'date': revision_tmstamp}
        conn = get_connection(params)
        if path == '/':
            containers = [conn.cont_cls.from_path(conn, path)]
        else:
            containers = conn.get_containers(container_path)
        # Q2: Get objects for instant list, plus one to check "next".
        container = [c for c in containers if c.base_path == path][0]
        objects = container.get_objects(object_path, None, 1000000)
    except Exception:
        raise Http404("Revision or folder not found")

    tag_list = conn.get_tag_list()
    limit = settings.CLOUD_BROWSER_DEFAULT_LIST_LIMIT
    page_int = int(page)
    init_page = page_int * limit
    end_page = ((page_int + 1) * limit)
    if init_page >= len(tag_list):
        init_page -= limit
        end_page -= limit
    tag_list = tag_list[init_page:end_page]
    statistics = conn.get_statistics()
    closest_catalog_path = container.get_closest_catalog_path()[1:]
    current_tag = conn.get_tag_by_revision()
    revision_date = str(current_tag.timestamp.date())

    return render_to_response('cloud_browser/browser.html',
                              {'path': path,
                               'revision': revision,
                               'tag_list': tag_list,
                               'revision_date': revision_date,
                               'current_tag': current_tag,
                               'fqrn': repo_name,
                               'closest_catalog_path': closest_catalog_path,
                               'breadcrumbs': _breadcrumbs(path),
                               'page': page,
                               'statistics': statistics,
                               'container_path': container_path,
                               'containers': containers,
                               'container': container,
                               'object_path': object_path,
                               'objects': objects},
                              context_instance=RequestContext(request))


@settings_view_decorator
def document(request, repo_name, revision, path):
    """View single document from path.

    :param path: Path to resource, including container as first part of path.
    """
    user_data = httpagentparser.detect(request.META['HTTP_USER_AGENT'])
    if 'browser' not in user_data:
        return HttpResponseBadRequest()

    path = urllib.unquote(path)
    container_path, object_path = path_parts(path)
    url = settings.CLOUD_BROWSER_CVMFS_URL_MAPPING[repo_name]

    params = {'url': url, 'revision': revision, 'date': None}
    conn = get_connection(params)
    try:
        container = conn.get_container(container_path)
    except errors.NoContainerException:
        raise Http404("No container at: %s" % container_path)
    except errors.NotPermittedException:
        raise Http404("Access denied for container at: %s" % container_path)

    try:
        storage_obj = container.get_object(object_path)
    except errors.NoObjectException:
        raise Http404("No object at: %s" % object_path)

    # Get content-type and encoding.
    local_path = storage_obj.local_path()
    content_type = None
    if local_path:
        content_type = magic.from_file(local_path, mime=True)
    encoding = storage_obj.smart_content_encoding
    response = HttpResponse(content=storage_obj.read(),
                            content_type=content_type)
    if encoding not in (None, ''):
        response['Content-Encoding'] = encoding

    return response

@settings_view_decorator
def diff(request, repo_name, revision1, revision2, path):
    """Compare two documents in different revisions for a given path"""

    user_data = httpagentparser.detect(request.META['HTTP_USER_AGENT'])
    if 'browser' not in user_data:
        return HttpResponseBadRequest()

    contents = []
    path = urllib.unquote(path)
    container_path, object_path = path_parts(path)
    url = settings.CLOUD_BROWSER_CVMFS_URL_MAPPING[repo_name]
    content_type = 'text/*'
    for revision in [revision1, revision2]:
        params = {'url': url, 'revision': revision, 'date': None}
        conn = get_connection(params)
        try:
            container = conn.get_container(container_path)
        except errors.NoContainerException:
            raise Http404("No container at: %s" % container_path)
        except errors.NotPermittedException:
            raise Http404("Access denied for container at: %s" % container_path)

        try:
            storage_obj = container.get_object(object_path)
        except errors.NoObjectException:
            raise Http404("No object at: %s" % object_path)
        content_type = magic.from_file(storage_obj.local_path(), mime=True)
        contents.append(storage_obj.read())

    differ = difflib.HtmlDiff(tabsize=4, wrapcolumn=80)
    if 'text/' in content_type:
        final_diff_text = differ.make_table(
            fromdesc=str(revision1),
            todesc=str(revision2),
            fromlines=contents[0].split('\n'),
            tolines=contents[1].split('\n')
        )
    else:
        final_diff_text = 'The file contains binary data and cannot be processed'

    return render(request, 'cloud_browser/comparison.html',
                  {'table': final_diff_text})
