FROM python:3.11

RUN mkdir /sitevideo

WORKDIR /sitevideo

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
