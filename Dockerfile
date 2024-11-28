FROM python:3.9

RUN apt-get update && apt-get install -y build-essential

WORKDIR /pcm
