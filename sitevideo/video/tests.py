
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse


from video.models import VideoFile


# Тест кейс для проверки создания новой записи в базе данных
class VideoFileCreateAPIViewTest(APITestCase):
    def setUp(self):
        self.create_url = reverse('api:video-create')

    def test_create_video_file_with_valid_data(self):
        self.uploaded_file = SimpleUploadedFile("test_video.mp4", b"file_content", content_type="video/mp4")

        invalid_data = {'filename': 'video2', 'filepath': self.uploaded_file}
        response = self.client.post(self.create_url, invalid_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_video_file_with_invalid_data(self):
        uploaded_file = SimpleUploadedFile("test_video.avi", b"file_content", content_type="video/avi")

        invalid_data = {'filename': 'video2', 'filepath': uploaded_file}
        response = self.client.post(self.create_url, invalid_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# Кейс для тестирования GET, PATCH, DELETE запросов в классе VideoFileListAPIView
class VideoFileListAPIViewTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем временный файл для теста
        cls.uploaded_file = SimpleUploadedFile("test_video.mp4", b"file_content", content_type="video/mp4")
        # Создаем объект VideoFile с использованием созданного файла
        cls.video = VideoFile.objects.create(filename='video1', filepath=cls.uploaded_file)
        # Создаем URL для доступа к созданному объекту VideoFile
        cls.list_url = reverse('api:video-file-detail', kwargs={'pk': cls.video.id})

    def test_get_video_file(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_video_file_invalid_id(self):
        non_existing_list_url = reverse('api:video-file-detail',
                                        kwargs={'pk': 'daba8b08-a613-493d-b09f-5e7c390b3029'})
        response = self.client.get(non_existing_list_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_video_file(self):
        response = self.client.delete(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
