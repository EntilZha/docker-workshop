from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^view$', views.view, name='view'),
    url(r'^save$', views.save, name='save'),
    url(r'^show$', views.show, name='show')
]

