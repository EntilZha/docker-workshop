from django.conf.urls import url
from places import views

urlpatterns = [
    url(r'^$', views.index, name='index')
]
