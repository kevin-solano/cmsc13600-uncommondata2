from django.urls import path
from . import views

urlpatterns = [
    #HW1-2
    path("time", views.app_time),
    path('sum', views.app_sum),
    # HTML page: form for new user
    path('new/', views.new_user, name='new_user'),
    # API endpoint: form submission
    path('api/createUser/', views.create_user, name='create_user'),
    # HTML View: login required
    path('uploads/', views.uploads_page, name='uploads_page'),
    ###### API Endpoints #####
    # creates Upload object in database
    path('api/upload/', views.api_upload, name='api_upload'),
    ### API: GET -> JSON ###
    path('api/dump-uploads/', views.dump_uploads, name='dump_uploads'),
    # curator inspection of Facts table
    path('api/dump-data/', views.dump_data, name='dump_data'),
    # public APi, joke
    path('api/knock-knock/', views.knock_knock, name='knockknock'),
]