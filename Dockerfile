FROM python:3.10

RUN apt-get update && apt-get install -y build-essential

WORKDIR /pcm
