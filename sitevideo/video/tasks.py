import ffmpeg

from sitevideo.celery import celery
import os

import logging

logger = logging.getLogger('main')


@celery.task
def resize_video(instance_id, input_file_path, output_file_path, width, height):
    from sitevideo.settings import MEDIA_ROOT
    from .models import VideoFile
    # Создаем модель текущего объекта из БД
    instance = VideoFile.objects.get(id=instance_id)

    try:
        ffmpeg.input(input_file_path).output(output_file_path, s=f'{width}x{height}').run(overwrite_output=True)

        instance.processingSuccess = True
        logger.info(f"Video processing has started. ID: {instance_id}")
        return True

    except Exception as e:
        instance.processing = False
        instance.processingSuccess = False
        logger.error(f"An error occurred while processing the video. ID: {instance_id}")
        return False

    finally:
        instance.processing = False

        # Приводим новый путь к файлу к относительному виду
        final_file_path = os.path.relpath(output_file_path, MEDIA_ROOT)

        # Нормализуем путь
        final_file_path = final_file_path.replace("\\", "/")

        instance.filepath = final_file_path

        os.remove(input_file_path)

        instance.save()

        logger.info(f"Video processing completed. ID: {instance_id}")