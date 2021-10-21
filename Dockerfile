FROM ubuntu:latest

RUN apt update && apt upgrade -y
RUN apt install python3 python3-venv python3-pip -y

WORKDIR /code

COPY requirements.txt /code/
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /code/
COPY ./ /code/

RUN python3 app.py