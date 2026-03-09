"""URL configuration for uncommondata project cont.
app.urls
"""
from django.urls import path
from . import views

urlpatterns = [
    # HW 1-2
    path("time", views.app_time),
    path('sum', views.app_sum),
    # HTML page: form for new user
    path('new/', views.new_user, name='new_user'),
    # API endpoint: new user form submission
    path('api/createUser/', views.create_user, name='create_user'),
    # HTML View: login required
    path('uploads/', views.uploads, name='uploads_page'),
    # public API, joke
    path('api/knockknock/', views.knock_knock, name='knockknock'),
    ################ API Endpoints ################
    # creates Upload object in database
    path('api/upload/', views.api_upload, name='api_upload'),
    # API Endpoint: GET request, returns data about all uploads of given user -> JSON
    path('api/dump-uploads/', views.dump_uploads, name='dump_uploads'),
    # curator inspection of Facts table
    path('api/dump-data/', views.dump_data, name='dump_data'),
    # HTML list of already uploaded files
    path('api/show-uploads/', views.show_uploads, name='show_uploads'),
    # GET: file download
    path('api/download/{ID}', views.show_uploads, name='download'),
    # GET endpoint: data extraction, return extracted data as JSOn
    path('/api/process/{ID}', views.show_uploads, name= 'process'),
]