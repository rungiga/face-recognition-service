FROM python:3.7.9-slim

RUN apt-get update && \
    apt-get install build-essential cmake pkg-config \
    libopenblas-dev liblapack-dev \
    libx11-dev libgtk-3-dev \
    ffmpeg libsm6 libxext6 -y

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY ./app /app

WORKDIR /app

EXPOSE 8080
ENTRYPOINT ["gunicorn", "app:app", "-b", "0.0.0.0:8080"]