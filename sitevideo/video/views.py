import ffmpeg

from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.response import Response

from sitevideo.settings import MEDIA_ROOT
from .models import VideoFile
from .serializers import VideoFileSerializer, VideoFileCreateSerializer
import os

from .tasks import resize_video


class VideoFileListAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VideoFile.objects.all()
    serializer_class = VideoFileSerializer

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        filtered_data = {
            'id': data['id'],
            'filename': data['filename'],
            'processing': data['processing'],
            'processingSuccess': data['processingSuccess']
        }
        return Response(filtered_data)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        file_path = instance.filepath.path
        self.perform_destroy(instance)

        if os.path.exists(file_path):
            os.remove(file_path)
        response_data = {'success': True}

        return Response(response_data, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        width = request.data.get('width')
        height = request.data.get('height')

        # Проверка на корректность полученных данных width и height
        if not (width and height and isinstance(width, int) and isinstance(height, int) and width > 20 and height > 20):
            return JsonResponse({'error': 'Неверные данные для изменения разрешения'},
                                status=status.HTTP_400_BAD_REQUEST)

        # Устанавливаем статусы процесса обработки
        instance.processing = True
        instance.processingSuccess = False
        instance.save()

        # Получаем абсолютный входной путь файла
        input_file_path = str(instance.filepath.path)

        # Создаем выходной путь файла
        output_file_path = f'{os.path.splitext(input_file_path)[0]}_resized.mp4'

        # Запускаем таску для обработки видео
        resize_video.delay(instance.id, input_file_path, output_file_path, width, height)

        return JsonResponse({'success': True})


class VideoFileCreateAPIView(generics.CreateAPIView):
    queryset = VideoFile.objects.all()
    serializer_class = VideoFileCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_data = {'id': serializer.instance.id}
        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_200_OK)
