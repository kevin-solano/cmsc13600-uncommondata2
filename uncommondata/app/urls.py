from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello_xyz, name='hello_xyz'),
    path('new/', views.new_user, name='new_user'),  # This handles /app/new/
    path('api/createUser/', views.create_user, name='create_user'),  # This handles /app/api/createUser/
    path('uploads/', views.uploads, name='uploads'),
    path('api/dump-uploads/', views.dump_uploads, name='dump_uploads'),
    path('api/dump-data/', views.dump_data, name='dump_data'),
    path('api/knockknock/', views.knock_knock, name='knock_knock'),
]