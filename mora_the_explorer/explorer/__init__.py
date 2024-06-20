# This import is crucial (both that it happens and that it happens before the others) as
# without a running QCoreApplication instance all the threading and signals and so on
# will not work
from .appmanager import app, AppManager

# These are just namespace imports for convenience
from .config import Config
from .explorer import Explorer
