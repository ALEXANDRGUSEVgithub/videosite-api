from rest_framework import serializers

from video.models import VideoFile


class VideoFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoFile
        fields = ("__all__")


class VideoFileRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoFile
        fields = ('id', 'filename', 'processing', 'processingSuccess')