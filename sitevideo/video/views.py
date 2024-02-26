from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response

from .models import VideoFile
from .serializers import VideoFileSerializer, VideoFileRetrieveSerializer
import os


class VideoFileCreateAPIView(generics.ListCreateAPIView):
    queryset = VideoFile.objects.all()
    serializer_class = VideoFileSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        response_data = {'id': serializer.instance.id}

        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save()


class VideoFileGetUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VideoFile.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return VideoFileRetrieveSerializer
        return VideoFileSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        file_path = instance.filepath.path
        self.perform_destroy(instance)

        if os.path.exists(file_path):
            os.remove(file_path)

        return Response({'success': True})
