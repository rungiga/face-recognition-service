FROM python:3.7.9-slim

RUN apt-get update 
RUN apt-get install build-essential cmake pkg-config -y
RUN apt-get install libopenblas-dev liblapack-dev -y
RUN apt-get install libx11-dev libgtk-3-dev -y
RUN apt-get install ffmpeg libsm6 libxext6 -y

RUN pip3 install dlib

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY ./app /app

WORKDIR /app


ARG APP_PORT
ENV PORT=$APP_PORT

ARG APP_HOST
ENV HOST=$APP_HOST

EXPOSE $APP_PORT
RUN chmod +x start.sh
ENTRYPOINT [ "./start.sh" ]