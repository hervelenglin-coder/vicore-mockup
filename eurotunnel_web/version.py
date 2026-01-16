import importlib
from typing import Final


def get_version()->str:
    try:
        return importlib.metadata.version('eurotunnel_web')
    except:
        #so....when we run in the development container
        #poetry hasn't done it's thing and installed the package
        #so we can't get the version number.
        #In the prod container however it's fine.
        #If we really hate ourselves we *could* parse it out of pyproj.toml, but does it really matter?
        return 'dev'

VERSION: Final[str] =  get_version()