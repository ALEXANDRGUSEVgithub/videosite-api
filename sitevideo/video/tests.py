from django.test import TestCase

from video.models import VideoFile


# Create your tests here.
class TestTestCase(TestCase):

    def test(self):
        data = VideoFile.objects.all()
        if not data:
            raise Exception('Данные не найдены')