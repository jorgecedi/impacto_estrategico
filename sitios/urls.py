from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^import-from-csv', views.impport_from_csv, name='import_from_csv'),
    url(r'^download', views.download_csv_from_monitor, name='download'),
]
