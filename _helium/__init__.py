from helium.version import __version__
try:
    # ignore import errors for setup.py to be able to do it's work
    # pre-dependency installations
    from helium.service import Service
except:
    pass
