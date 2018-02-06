"""
Possible functions for the ``PRIVATE_STORAGE_AUTH_FUNCTION`` setting.
"""
import django

if django.VERSION >= (1, 10):
    def allow_authenticated(private_file):
        return private_file.request.user.is_authenticated

    def allow_staff(private_file):
        request = private_file.request
        return request.user.is_authenticated and request.user.is_staff

    def allow_superuser(private_file):
        request = private_file.request
        return request.user.is_authenticated and request.user.is_superuser
else:
    def allow_authenticated(private_file):
        return private_file.request.user.is_authenticated()

    def allow_staff(private_file):
        request = private_file.request
        return request.user.is_authenticated() and request.user.is_staff

    def allow_superuser(private_file):
        request = private_file.request
        return request.user.is_authenticated() and request.user.is_superuser
