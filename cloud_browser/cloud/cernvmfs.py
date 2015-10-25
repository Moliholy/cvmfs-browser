"""File-system datastore."""
from __future__ import with_statement

import os

from cloud_browser.app_settings import settings
from cloud_browser.cloud import errors, base
from cloud_browser.common import SEP

from cvmfs import Repository


###############################################################################
# Classes
###############################################################################
class CVMFilesystemContainerWrapper(errors.CloudExceptionWrapper):
    """Exception translator."""
    translations = {
        OSError: errors.NoContainerException,
    }
wrap_fs_cont_errors = CVMFilesystemContainerWrapper()  # pylint: disable=C0103


class CVMFilesystemObjectWrapper(errors.CloudExceptionWrapper):
    """Exception translator."""
    translations = {
        OSError: errors.NoObjectException,
    }
wrap_fs_obj_errors = CVMFilesystemObjectWrapper()  # pylint: disable=C0103


class CVMFilesystemObject(base.CloudObject):
    """CVMFilesystem object wrapper."""

    def __init__(self, container, name, full_path, content_hash, size, **kwargs):
        super(CVMFilesystemObject, self).__init__(container, name, **kwargs)
        self.content_hash = content_hash
        self.size = size
        self.full_path = full_path

    def _get_object(self):
        """Return native storage object."""
        return object()

    def _read(self):
        """Return contents of object."""
        with self.container.conn.repository.retrieve_object(self.content_hash) \
                as file_obj:
            return file_obj.read()

    @property
    def path(self):
        """Base absolute path of container."""
        return self.full_path

    @classmethod
    def from_path(cls, container, path):
        """Create object from path."""
        if not path.startswith(container.base_path):
            path = os.path.join(container.base_path, path)
        dirent = container.conn.repository.lookup(path)
        obj_type = cls.type_cls.SUBDIR if dirent.is_directory() \
            else cls.type_cls.FILE

        return cls(container,
                   name=dirent.name,
                   size=dirent.size,
                   full_path=path,
                   content_hash=dirent.content_hash,
                   content_type=None,
                   last_modified=dirent.mtime,
                   obj_type=obj_type)


class CVMFilesystemContainer(base.CloudContainer):
    """Filesystem container wrapper."""
    #: Storage object child class.
    obj_cls = CVMFilesystemObject

    def _get_container(self):
        """Return native container object."""
        return object()

    @wrap_fs_obj_errors
    def get_objects(self, path, marker=None,
                    limit=settings.CLOUD_BROWSER_DEFAULT_LIST_LIMIT):
        """Get objects."""
        def _filter(name):
            """Filter."""
            return ((marker is None or
                     os.path.join(path, name).strip(SEP) > marker.strip(SEP)))

        search_path = os.path.join(self.base_path, path)
        dir_names = [dirent.name for dirent in
                     self.conn.repository.list_directory(search_path)]
        objs = [self.obj_cls.from_path(self, os.path.join(search_path, o))
                for o in dir_names if _filter(o)]
        return objs[:limit]

    @wrap_fs_obj_errors
    def get_object(self, path):
        """Get single object."""
        return self.obj_cls.from_path(self, path)

    @property
    def base_path(self):
        """Base absolute path of container."""
        return os.path.join(SEP, self.name)

    @classmethod
    def from_path(cls, conn, path):
        """Create container from path."""
        path = path.strip(SEP)
        full_path = os.path.join(SEP, path)
        dirent = conn.repository.lookup(full_path)
        return cls(conn=conn, name=path, count=0, size=dirent.size)


class CVMFilesystemConnection(base.CloudConnection):
    """Filesystem connection wrapper."""
    #: Container child class.
    cont_cls = CVMFilesystemContainer

    def __init__(self, url, cache_dir):
        """Initializer."""
        super(CVMFilesystemConnection, self).__init__(None, None)
        if url not in opened_repositories:
            opened_repositories[url] = Repository(url, cache_dir)
        self.repository = opened_repositories[url]

    def _get_connection(self):
        """Return native connection object."""
        return object()

    @wrap_fs_cont_errors
    def _get_containers(self):
        """Return available containers."""
        # get the list of directories
        root_list = [dirent.name for dirent in
                     self.repository.list_directory('') if dirent.is_directory()]
        return [self.cont_cls.from_path(self, d) for d in root_list]

    @wrap_fs_cont_errors
    def _get_container(self, path):
        """Return single container."""
        return self.cont_cls.from_path(self, path)


opened_repositories = {}

