FROM python:3.10-slim
RUN apt-get update && apt-get install -y curl
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt