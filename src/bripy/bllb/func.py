import toolz


@toolz.curry
def flip(f, *args, **kwargs):
    return f(*reversed(args), **kwargs)
