from uuid import uuid4

from django.db import models


class VideoFile(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, verbose_name="UUID")
    filename = models.CharField(max_length=255, verbose_name="Название файла")
    processing = models.BooleanField(default=False, verbose_name='Идет ли процесс обработки')
    processingSuccess = models.BooleanField(default=None, null=True,
                                            verbose_name="Успешность последней операции над видео")
    filepath = models.FileField(upload_to='video_file/')

