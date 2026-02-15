from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello_xyz, name='hello_xyz'),
    path('new/', views.new_user, name='new_user'),
    path('api/createUser/', views.create_user, name='create_user'),
    path('uploads/', views.uploads, name='uploads'),
    path('api/dump-uploads/', views.dump_uploads, name='dump_uploads'),
]