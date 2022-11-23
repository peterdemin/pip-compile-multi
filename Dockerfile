FROM ubuntu:20.04

RUN apt-get update -y && apt-get install -y python3.8-venv make

WORKDIR /pcm
