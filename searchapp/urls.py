from django.urls import path
from .views import search_view
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('search/', search_view, name='search'),
]
