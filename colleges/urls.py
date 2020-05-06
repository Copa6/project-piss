from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.get_links, name='college_links'),
    path('create/', views.create_college, name='create_college'),
    path('get-all-colleges', views.get_all_colleges, name='all_colleges'),
    path('search/<str:city_id>', views.get_all_colleges_for_city, name='all_colleges_for_city'),
    path('cities', views.get_all_cities, name='all_cities'),
]
