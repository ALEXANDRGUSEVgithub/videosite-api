from django.http import JsonResponse, Http404
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import VideoFile
from .serializers import VideoFileSerializer, VideoFileCreateSerializer
import os

from .tasks import resize_video

import logging

logger = logging.getLogger('main')


class VideoFileListAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VideoFile.objects.all()
    serializer_class = VideoFileSerializer

    def get(self, request, *args, **kwargs):
        try:
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

        except Http404:
            logger.error("Video file not found")
            return Response({"error": 'Video file not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"An error occurred in VideoFileListAPIView: {e}")
            return Response({"error": 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            file_path = instance.filepath.path
            self.perform_destroy(instance)

            if os.path.exists(file_path):
                os.remove(file_path)

            response_data = {'success': True}

            return Response(response_data, status=status.HTTP_204_NO_CONTENT)

        except Http404:
            logger.error("The file cannot be deleted because the file was not found")
            return Response({"error": 'The file cannot be deleted because the file was not found'},
                            status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"An error occurred in VideoFileListAPIView: {e}")
            return Response({"error": 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            width = request.data.get('width')
            height = request.data.get('height')

            # Проверка на корректность полученных данных width и height
            if not (width and height and isinstance(width, int) and isinstance(height, int) and width > 20 and height > 20):
                raise ValidationError()

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

        except Http404:
            logger.error("There is no file with this id")
            return Response({"error": 'There is no file with this id'},
                            status=status.HTTP_404_NOT_FOUND)

        except ValidationError as ve:
            logger.error('Invalid width and height data')
            return Response({"error": "Invalid width and height data"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception("An error occurred in patch method")
            return JsonResponse({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VideoFileCreateAPIView(generics.CreateAPIView):
    queryset = VideoFile.objects.all()
    serializer_class = VideoFileCreateSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)

            serializer.is_valid(raise_exception=True)
            serializer.save()

            response_data = {'id': serializer.instance.id}
            headers = self.get_success_headers(serializer.data)
            logger.info(f"A new record has been created in the database with id: {serializer.instance.id}")
            return Response(response_data, status=status.HTTP_200_OK)

        except ValidationError as ve:
            logger.error("Invalid file format")
            return Response({"error": 'Invalid file format'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"An error occurred in VideoFileCreateAPIView: {e}")
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)