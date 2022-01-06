#!/bin/bash

gunicorn app:app -b $HOST:$PORT