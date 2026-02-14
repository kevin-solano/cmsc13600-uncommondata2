from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello_xyz, name='hello_xyz'),
    path('new/', views.new_user, name='new_user'),  # This handles /app/new/
    path('api/createUser/', views.create_user, name='create_user'),  # This handles /app/api/createUser/
    path('time/', views.current_time, name='current_time'),
    path('sum/', views.sum_numbers, name='sum_numbers'),
]