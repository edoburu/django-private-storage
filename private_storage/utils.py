from django.core.exceptions import ImproperlyConfigured

try:
    from importlib import import_module  # Python 2.7+
except ImportError:
    from django.utils.importlib import import_module


def import_symbol(import_path):
    """
    Import a class or attribute by name.
    """
    try:
        dot = import_path.rindex('.')
    except ValueError:
        raise ImproperlyConfigured("{0} isn't a Python path.".format(import_path))

    module, classname = import_path[:dot], import_path[dot + 1:]
    try:
        mod = import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured('Error importing module {0}: "{1}"'.format(module, e))

    try:
        return getattr(mod, classname)
    except AttributeError:
        raise ImproperlyConfigured('Module "{0}" does not define a "{1}" class.'.format(module, classname))
