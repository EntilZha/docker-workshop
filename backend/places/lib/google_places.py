from googleplaces import GooglePlaces
from backend.settings import settings
from django.core.cache import cache


def nearby_search(keywords, location):
    cache_key = str((keywords, location))
    results = cache.get(cache_key)
    if results is not None:
        return results
    print "Google Places API Hit"
    google_places = GooglePlaces(settings.GOOGLE_PLACES_API_KEY)
    api_results = google_places.nearby_search(
        radius=25000,
        location=location,
        keyword=keywords
    )
    results = map(lambda p: p.name, api_results.places)
    cache.set(cache_key, results)
    return results
