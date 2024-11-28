FROM ubuntu:24.04

RUN apt-get update -y && apt-get install -y python3.9-venv make

WORKDIR /pcm
