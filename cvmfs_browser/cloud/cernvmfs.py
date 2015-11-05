"""File-system datastore."""
from __future__ import with_statement

import os

from cvmfs_browser.app_settings import settings
from cvmfs_browser.cloud import errors, base
from cvmfs_browser.common import SEP

from cvmfs import Repository
from cvmfs.dirent import ContentHashTypes


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

    def __init__(self, container, name, full_path, content_hash,
                 content_hash_type, size, **kwargs):
        super(CVMFilesystemObject, self).__init__(container, name, **kwargs)
        self.content_hash = content_hash
        self.content_hash_type = content_hash_type
        self.size = size
        self.full_path = full_path
        self.is_nested_catalog_mountpoint = kwargs['is_nested_catalog_mountpoint'] \
            if 'is_nested_catalog_mountpoint' in kwargs else False

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
    def from_dirent(cls, container, dirent):
        from datetime import datetime

        obj_type = cls.type_cls.SUBDIR if dirent.is_directory() \
            else cls.type_cls.FILE
        formatted_date = datetime.fromtimestamp(dirent.mtime)
        hash_type = ContentHashTypes.to_string(dirent.content_hash_type)

        return cls(container,
                   name=dirent.name,
                   size=dirent.size,
                   full_path=os.path.join(container.base_path, dirent.name),
                   content_hash=dirent.content_hash,
                   content_hash_type=hash_type,
                   content_type=None,
                   last_modified=formatted_date,
                   obj_type=obj_type,
                   is_nested_catalog_mountpoint=dirent.is_nested_catalog_mountpoint())

    @classmethod
    def from_path(cls, container, path):
        """Create object from path."""
        from datetime import datetime

        if not path.startswith(container.base_path):
            path = os.path.join(container.base_path, path)
        dirent = container.conn.repository.lookup(path)
        obj_type = cls.type_cls.SUBDIR if dirent.is_directory() \
            else cls.type_cls.FILE
        formatted_date = datetime.fromtimestamp(dirent.mtime)
        hash_type = ContentHashTypes.to_string(dirent.content_hash_type)

        return cls(container,
                   name=dirent.name,
                   size=dirent.size,
                   full_path=path,
                   content_hash=dirent.content_hash,
                   content_hash_type=hash_type,
                   content_type=None,
                   last_modified=formatted_date,
                   obj_type=obj_type)


class CVMFilesystemContainer(base.CloudContainer):
    """Filesystem container wrapper."""
    #: Storage object child class.
    obj_cls = CVMFilesystemObject

    def _get_container(self):
        """Return native container object."""
        return object()

    @wrap_fs_obj_errors
    def get_objects(self, path, marker=None, limit=1000000):
        """Get objects."""
        search_path = self.base_path
        dirents = [dirent for dirent in
                   self.conn.repository.list_directory(search_path)
                   if not dirent.is_symlink()]
        objs = [self.obj_cls.from_dirent(self, o) for o in dirents]
        return objs

    @wrap_fs_obj_errors
    def get_object(self, path):
        """Get single object."""
        return self.obj_cls.from_path(self, path)

    def get_closest_catalog_path(self):
        return self.conn.repository  \
            .retrieve_catalog_for_path(self.base_path).root_prefix

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

    def __init__(self):
        """Initializer."""
        super(CVMFilesystemConnection, self).__init__(None, None)
        self.repository = None
        self.revision = None

    def configure(self, url, revision, timestamp,
                  cache_dir=settings.CLOUD_BROWSER_CVMFS_CACHE):
        if url not in opened_repositories:
            opened_repositories[url] = Repository(url, cache_dir)
            self.repository = opened_repositories[url]
        if timestamp:
            history = self.repository.retrieve_history()
            self.revision = history.get_tag_by_date(timestamp).revision
        else:
            self.revision = revision \
                if revision != 'latest' else self.repository.manifest.revision
            if revision != 'latest':
                self.repository.switch_revision(self.revision)

    def get_tag_list(self):
        history = self.repository.retrieve_history()
        if history:
            return history.list_tags()

    def get_tag_by_revision(self):
        history = self.repository.retrieve_history()
        if history:
            return history.get_tag_by_revision(self.revision)

    def _get_connection(self):
        """Return native connection object."""
        return object()

    def get_statistics(self):
        return self.repository.retrieve_root_catalog() \
            .get_statistics().get_all_fields()

    @wrap_fs_cont_errors
    def _get_containers(self, path='/'):
        """Return available containers."""
        # get the list of directories
        path = '/' if not path else path
        root_list = [os.path.join(path, dirent.name) for dirent in
                     self.repository.list_directory(path)
                     if dirent.is_directory() and not dirent.is_symlink()]
        return [self.cont_cls.from_path(self, d) for d in root_list]

    @wrap_fs_cont_errors
    def _get_container(self, path):
        """Return single container."""
        return self.cont_cls.from_path(self, path)


opened_repositories = {}

