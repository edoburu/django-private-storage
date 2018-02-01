"""
Possible functions for the ``PRIVATE_STORAGE_AUTH_FUNCTION`` setting.
"""


def allow_authenticated(private_file):
    try:
        return private_file.request.user.is_authenticated()
    except AttributeError:
        # Using user.is_authenticated() and user.is_anonymous() as a method is deprecated since Django 2.0
        return private_file.request.user.is_authenticated
    

def allow_staff(private_file):
    request = private_file.request
    try:
        return request.user.is_authenticated() and request.user.is_staff
    except AttributeError:
        # Using user.is_authenticated() and user.is_anonymous() as a method is deprecated since Django 2.0
        return request.user.is_authenticated and request.user.is_staff


def allow_superuser(private_file):
    request = private_file.request
    try:
        return request.user.is_authenticated() and request.user.is_superuser
    except AttributeError:
        # Using user.is_authenticated() and user.is_anonymous() as a method is deprecated since Django 2.0
        return request.user.is_authenticated and request.user.is_superuser
