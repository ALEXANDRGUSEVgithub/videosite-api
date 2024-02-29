#!/bin/bash


celery --app=sitevideo.sitevideo.celery:celery worker -l INFO
