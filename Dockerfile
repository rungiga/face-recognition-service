FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install build-essential cmake pkg-config \
    libopenblas-dev liblapack-dev \
    libx11-dev libgtk-3-dev \
    ffmpeg libsm6 libxext6 \
    python3-wheel python3-werkzeug python3-pip \
    python3-flask gunicorn python3-opencv \
    python3-aniso8601 \
    python3-jsonschema python3-zipp python3-pyrsistent -y

COPY requirements.txt /
RUN pip3 install --no-cache-dir --prefer-binary -r /requirements.txt

COPY ./app /app

WORKDIR /app

EXPOSE 8080
ENTRYPOINT ["gunicorn", "app:app", "-b", "0.0.0.0:8080"]