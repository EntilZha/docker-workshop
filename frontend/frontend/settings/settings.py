import os
from frontend.settings.common import *

if os.getenv('DJANGO_MODE') == 'production':
    from frontend.settings.production import *
else:
    from frontend.settings.development import *