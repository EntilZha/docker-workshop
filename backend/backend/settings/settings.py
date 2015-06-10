import os
from backend.settings.common import *

if os.getenv('DJANGO_MODE') == 'production':
    from backend.settings.production import *
else:
    from backend.settings.development import *