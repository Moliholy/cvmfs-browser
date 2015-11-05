"""Cloud abstractions and helpers.

More generally, this is "datastore" support, since the basic interface could
support any interface, file, memory, cloud, etc. But, as this is called a
"cloud" browser, we'll call it the "cloud" module.
"""


def get_connection(params):
    """Return global connection object.

    :rtype: :class:`cloud_browser.cloud.base.CloudConnection`
    """
    from cvmfs_browser.cloud.config import Config
    return Config.get_connection(params)


def get_connection_cls():
    """Return global connection class.

    :rtype: :class:`type`
    """
    from cvmfs_browser.cloud.config import Config
    return Config.get_connection_cls()
