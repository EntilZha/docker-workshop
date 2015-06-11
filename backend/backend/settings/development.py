print "Running in Development Mode"

SECRET_KEY = 'us6+ep@v2#d!m($emoy4%e!@6*c6mryowq9$9qr2c&-6(p*6)-'

DEBUG = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
