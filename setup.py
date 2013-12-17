from setuptools import setup, find_packages

PACKAGE = 'varify'
VERSION = __import__(PACKAGE).get_version()

install_requires = [
    'django>=1.4.4,<1.5',
    'markdown==2.1.1',
    'south==0.8.2',
    'python-memcached==1.48',
    'coverage',
    'raven>=3.3.9',
    'uwsgi',
    'rq>=0.3.8',
    'django-rq>=0.5.1',
    'rq-dashboard>=0.3.1',
    'django-rq-dashboard',
    'django-widget-tweaks',
    'psycopg2==2.4.4',
    'avocado==2.0.24',
    'serrano==2.0.16',
    'cilantro>=2.0.11,<2.1',
    'modeltree>=1.1.7',
    'django-haystack==1.2.7',
    'whoosh==2.4.0',
    'openpyxl==1.6.1',
    'django-siteauth==0.9b1',
    'python-ldap>=2.3.12,<2.4',
    'django-registration2==0.9b2',
    'django-tracking2==0.1.2',
    'django-bootstrap-form>=0.5',
    'django-guardian==1.0.4',
    'django-sts==0.7.3',
    'pycap==0.8.1',
    'django-reversion==1.6.6',
    'diff-match-patch',
    'vcf==0.6.5',
    'django-news',
]

kwargs = {
    'name': PACKAGE,
    'version': VERSION,
    'packages': find_packages(exclude=['tests', '*.tests', '*.tests.*',
                                       'tests.*']),
    'install_requires': install_requires,
    # This is a hack to get setuptools to install the the latest version of
    # PyVCF from the github repo. This version doesn't yet exist on pypi so the
    # so the entry install_requires won't find anything and it will fall back
    # to this github link.
    'dependency_links': [
        'https://github.com/jamescasbon/PyVCF/archive/master.zip#egg=vcf-0.6.5',
    ],
    'test_suite': 'test_suite',
    'author': '',
    'author_email': '',
    'description': '',
    'license': '',
    'keywords': '',
    'url': '',
    'classifiers': [],
}

setup(**kwargs)
