#!/usr/bin/env python
import sys
from django.conf import settings, global_settings as default_settings
from django.core.management import execute_from_command_line
from os import path

if not settings.configured:
    module_root = path.dirname(path.realpath(__file__))

    settings.configure(
        DEBUG=False,  # will be False anyway by DjangoTestRunner.
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        },
        INSTALLED_APPS=(
            'private_storage',
        ),
        TEST_RUNNER='django.test.runner.DiscoverRunner',
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': (),
                'OPTIONS': {
                    'loaders': (
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                    ),
                    'context_processors': (
                        'django.template.context_processors.debug',
                        'django.template.context_processors.i18n',
                        'django.template.context_processors.media',
                        'django.template.context_processors.request',
                        'django.template.context_processors.static',
                        'django.contrib.auth.context_processors.auth',
                    ),
                },
            },
        ],
        AWS_PRIVATE_STORAGE_BUCKET_NAME='foobar',
        PRIVATE_STORAGE_ROOT=path.join(module_root, 'test-media-root'),
    )


def runtests():
    argv = sys.argv[:1] + ['test', 'private_storage'] + sys.argv[1:]
    execute_from_command_line(argv)


if __name__ == '__main__':
    runtests()
