from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_page
from jsonview.decorators import json_view
from jsonview.exceptions import BadRequest
from backend.settings import settings
from googleplaces import GooglePlaces


@cache_page(60 * 5)
@json_view
@require_GET
def index(request):
    print "Places backend reached"
    google_places = GooglePlaces(settings.GOOGLE_PLACES_API_KEY)
    keywords = request.GET.get('keywords')
    location = request.GET.get('location')
    if keywords is None or location is None:
        raise BadRequest('Must include keywords and location')
    results = google_places.nearby_search(
        radius=25000,
        location=location,
        keyword=keywords
    )
    return map(lambda p: p.name, results.places)
