"""Cloud browser views."""
import os
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.importlib import import_module

from cloud_browser.app_settings import settings
from cloud_browser.cloud import get_connection, get_connection_cls, errors
from cloud_browser.common import get_int, \
    path_parts, path_join, path_yield, relpath


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


@settings_view_decorator
def browser(request, repo_name, revision='latest', path='', template='cloud_browser/browser.html'):
    """View files in a file path.

    :param request: The request.
    :param path: Path to resource, including container as first part of path.
    :param template: Template to render.
    """

    # Inputs.
    path = '/' + path if not os.path.isabs(path) else path
    container_path, object_path = path_parts(path)
    incoming = request.POST or request.GET or {}
    page = incoming['page'] if 'page' in incoming else '0'

    # check the validity of the parameters
    if repo_name in settings.CLOUD_BROWSER_CVMFS_FQRN_WHITELIST:
        domain_pos = repo_name.find('.')
        domain = repo_name[domain_pos:]
        url = settings.CLOUD_BROWSER_CVMFS_URL_MAPPING[domain] \
            + repo_name[:domain_pos]
    else:
        return Http404('The repository %s is not allowed', repo_name)

    # Q1: Get all containers.
    #     We optimize here by not individually looking up containers later,
    #     instead going through this in-memory list.
    # TODO: Should page listed containers with a ``limit`` and ``marker``.
    try:
        params = {'url': url, 'revision': revision}
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

    return render_to_response(template,
                              {'path': path,
                               'revision': revision,
                               'revision_number': conn.revision,
                               'tag_list': tag_list,
                               'fqrn': repo_name,
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
def document(_, repo_name, revision, path):
    """View single document from path.

    :param path: Path to resource, including container as first part of path.
    """
    container_path, object_path = path_parts(path)
    # check the validity of the parameters
    if repo_name in settings.CLOUD_BROWSER_CVMFS_FQRN_WHITELIST:
        domain_pos = repo_name.find('.')
        domain = repo_name[domain_pos:]
        url = settings.CLOUD_BROWSER_CVMFS_URL_MAPPING[domain] \
              + repo_name[:domain_pos]
    else:
        return Http404('The repository %s is not allowed', repo_name)
    params = {'url': url, 'revision': revision}
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
    content_type = storage_obj.smart_content_type
    encoding = storage_obj.smart_content_encoding
    response = HttpResponse(content=storage_obj.read(),
                            content_type=content_type)
    if encoding not in (None, ''):
        response['Content-Encoding'] = encoding

    return response
