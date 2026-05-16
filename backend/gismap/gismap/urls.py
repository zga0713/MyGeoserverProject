from django.contrib import admin
from django.urls import path
from . import geoserver

urlpatterns = [
    path('admin/', admin.site.urls),
    path('get/', geoserver.get, name='get'),
    path('gethtml/', geoserver.gethtml, name='gethtml'),
    path('posthtml/', geoserver.posthtml, name='posthtml'),
    path('getwmts/', geoserver.wmts, name='getwmts'),
    path('getfeature/', geoserver.getfeature, name='getfeature'),
    path('postgml/', geoserver.postgml, name='postgml'),
    path('wfs/', geoserver.wfs_proxy, name='wfs'),
    path('geoserver/', geoserver.geoserverget, name='geoserver'),
    path('geoserverpost/', geoserver.geoserverpost, name='geoserverpost'),
]
