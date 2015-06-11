from django.views.decorators.http import require_GET
from jsonview.decorators import json_view
from jsonview.exceptions import BadRequest
from api.models import Place
from django.utils import timezone
import requests
import os


BACKEND_API_URL = 'http://{0}:80/places'.format(os.getenv('HOST_IP'))
#BACKEND_API_URL = 'http://backendweb:8000/places'


def nearby_places(location, keywords):
    params = {'location': location, 'keywords': keywords}
    places = requests.get(BACKEND_API_URL, params=params)
    return places.json()


@json_view
@require_GET
def view(request):
    if request.GET.get('location') is None or request.GET.get('keywords') is None:
        raise BadRequest('Missing location or keywords parameter')
    places = nearby_places(request.GET.get('location'), request.GET.get('keywords'))
    return places


@json_view
@require_GET
def save(request):
    if request.GET.get('location') is None or request.GET.get('keywords') is None:
        raise BadRequest('Missing location or keywords parameter')
    places = nearby_places(request.GET.get('location'), request.GET.get('keywords'))
    for p in places:
        db_place = Place(name=p, date_saved=timezone.now())
        db_place.save()
    return places


@json_view
def show(request):
    return map(lambda p: {'name': p.name, 'date_saved': p.date_saved}, Place.objects.all())
