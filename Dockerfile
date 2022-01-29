FROM python:3.8-slim

RUN apt-get update && \
    apt-get install build-essential cmake pkg-config \
    libopenblas-dev liblapack-dev \
    libx11-dev libgtk-3-dev \
    ffmpeg libsm6 libxext6 -y

COPY requirements.txt .
RUN pip3 install --no-cache-dir --prefer-binary -r requirements.txt

COPY ./app /app

WORKDIR /app

EXPOSE 8080
ENTRYPOINT ["gunicorn", "app:app", "-b", "0.0.0.0:8080"]