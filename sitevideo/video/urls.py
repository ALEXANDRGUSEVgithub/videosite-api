from django.urls import path
from video.views import *

app_name = "video"

urlpatterns = [
    path('file/', VideoFileCreateAPIView.as_view(), name='video-file-list-create'),
    path('file/<uuid:pk>/', VideoFileListAPIView.as_view(), name='video-file-detail')
]

