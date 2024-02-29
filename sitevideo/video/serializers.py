from pathlib import Path

from django.http import JsonResponse
from rest_framework import serializers, status

from video.models import VideoFile


class VideoFileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoFile
        fields = ("filename", "filepath")

    def validate(self, data):
        filename = data.get('filepath')
        filesuffix = Path(str(filename)).suffix
        if not filesuffix == '.mp4':
            raise serializers.ValidationError({'error': 'Invalid file format'})
        return data


class VideoFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoFile
        fields = ('__all__')