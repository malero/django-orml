from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',
        view=views.Dashboard.as_view(),
        name='orml-dashboard'),
]
