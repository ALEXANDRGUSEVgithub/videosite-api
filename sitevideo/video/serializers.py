from pathlib import Path

from rest_framework import serializers

from video.models import VideoFile


class VideoFileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoFile
        fields = ("filename", "filepath")

    def validate(self, data):
        filename = data.get('filepath')
        filesuffix = Path(str(filename)).suffix
        if not filesuffix == '.mp4':
            raise serializers.ValidationError({'error': 'Неверный формат файла'})
        return data


class VideoFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoFile
        fields = ('__all__')