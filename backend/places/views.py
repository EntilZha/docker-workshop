from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_page
from jsonview.decorators import json_view
from jsonview.exceptions import BadRequest
from places.lib.google_places import nearby_search


@cache_page(60 * 5)
@json_view
@require_GET
def index(request):
    print "Places backend reached"
    keywords = request.GET.get('keywords')
    location = request.GET.get('location')
    if keywords is None or location is None:
        raise BadRequest('Must include keywords and location')
    return nearby_search(keywords, location)
