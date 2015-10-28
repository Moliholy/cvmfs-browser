"""Cloud configuration."""


class Config(object):
    """General class helper to construct connection objects."""
    __connection_obj = None
    __connection_cls = None
    __connection_fn = None

    @classmethod
    def from_settings(cls):
        """Create configuration from Django settings or environment."""
        from cloud_browser.app_settings import settings
        from django.core.exceptions import ImproperlyConfigured

        conn_cls = conn_fn = None
        datastore = settings.CLOUD_BROWSER_DATASTORE
        if datastore == 'CVMFilesystem':
            # Use Cvmfs
            from cloud_browser.cloud.cernvmfs import CVMFilesystemConnection
            conn_cls = CVMFilesystemConnection
            conn_fn = lambda: CVMFilesystemConnection()

        if conn_cls is None:
            raise ImproperlyConfigured(
                "No suitable credentials found for datastore: %s." %
                datastore)

        # Adjust connection function.
        conn_fn = staticmethod(conn_fn)

        # Directly cache attributes.
        cls.__connection_cls = conn_cls
        cls.__connection_fn = conn_fn

        return conn_cls, conn_fn

    @classmethod
    def get_connection_cls(cls):
        """Return connection class.

        :rtype: :class:`type`
        """
        if cls.__connection_cls is None:
            cls.__connection_cls, _ = cls.from_settings()
        return cls.__connection_cls

    @classmethod
    def get_connection(cls, params=None):
        """Return connection object.

        :rtype: :class:`cloud_browser.cloud.base.CloudConnection`
        """
        if cls.__connection_obj is None:
            if cls.__connection_fn is None:
                _, cls.__connection_fn = cls.from_settings()
            cls.__connection_obj = cls.__connection_fn()
        if params:
            cls.__connection_obj.configure(params['url'],
                                           params['revision'])
        return cls.__connection_obj
