"""
Django settings for browser project.

Generated by 'django-admin startproject' using Django 1.8.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ub46aq=1!vny=3oces5pzdg+ajbonwxm5&p(jf*8i*holie#g%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloud_browser',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'browser.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            '/templates/',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'browser.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

CLOUD_BROWSER_DEFAULT_LIST_LIMIT = 500

CLOUD_BROWSER_DATASTORE = "CVMFilesystem"
CLOUD_BROWSER_CVMFS_CACHE = os.path.join(BASE_DIR, 'cvmfs_cache')
CLOUD_BROWSER_CVMFS_FQRN_WHITELIST = [
    'atlas.cern.ch',
    'lhcb.cern.ch',
    'alice.cern.ch',
    'geant4.cern.ch',
    'cms.cern.ch',
    'mice.egi.eu',
    'na62.egi.eu',
    'wenmr.egi.eu',
    'phys-ibergrid.egi.eu',
    'ams.cern.ch',
    'belle.cern.ch',
    'boss.cern.ch',
    'grid.cern.ch',
    'sft.cern.ch',
    'na61.cern.ch',
    'atlas-condb.cern.ch',
    'atlas-nightlies.cern.ch',
    'ilc.desy.de',
    'bbp.epfl.ch',
    'cernvm-prod.cern.ch',
    'biomed.egi.eu',
    't2k.egi.eu',
    'alice-ocdb.cern.ch',
    'calice.desy.de',
    'hermes.desy.de',
    'hone.desy.de',
    'olymppus.desy.de',
    'xfel.desy.de',
    'zeus.desy.de',
    'vlemed.amc.nl',
    'aleph.cern.ch',
    'cvmfs-config.cern.ch',
    'cernatschool.egi.eu',
    'glast.egi.eu',
    'hyperk.egi.eu',
    'snoplus.egi.eu',
    'pheno.egi.eu',
    'lhcbdev.cern.ch',
    'oasis.opensciencegrid.org',
    'icecube.opensciencegrid.org',
    'fcc.cern.ch',
    'auger.egi.eu',
    'km3net.egi.eu',
    'soft.mugqic',
    'ref.mugqic',
    'ganga.cern.ch',
    'darkside.opensciencegrid.org',
    'des.opensciencegrid.org',
    'fermilab.opensciencegrid.org',
    'gm2.opensciencegrid.org',
    'lariat.opensciencegrid.org',
    'lsst.opensciencegrid.org',
    'minos.opensciencegrid.org',
    'mmu2e.opensciencegrid.org',
    'nova.opensciencegrid.org',
    'seaquest.opensciencegrid.org',
    'usatlast3.opensciencegrid.org',
    'moedal.cern.ch',
    'cms-ib.cern.ch',
    'opal.cern.ch',
    'test.cern.ch',
    'na49.cern.ch',
    'pravda.egi.eu',
    'ghost.egi.eu',
]

CLOUD_BROWSER_CVMFS_URL_MAPPING = {
    '.cern.ch': 'http://cvmfs-stratum-one.cern.ch/opt/',
    '.desy.de': 'http://cvmfs-stratum-one.cern.ch/cvmfs/',
    '.egi.eu': 'http://cvmfs-egi.gridpp.rl.ac.uk:8000/cvmfs/',
    'amc.nl': 'http://cvmfs01.nikhef.nl/cvmfs/',
    '.opensciencegrid.org': 'http://cvmfs.racf.bnl.gov/cvmfs/',
}
