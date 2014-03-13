

class classproperty(object):
    """
    A mix out of the built-in `classmethod` and
    `property` so that we can achieve a property
    that is not bound to an instance.

    Example::

        >>> class Foo(object):
        ...     bar = 'baz'
        ...
        ...     @classproperty
        ...     def bars(cls):
        ...         return [cls.bar]
        ...
        >>> Foo.bars
        ['baz']
    """

    def __init__(self, func, name=None):
        self.func = func
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = func.__doc__

    def __get__(self, desc, cls):
        value = self.func(cls)
        return value