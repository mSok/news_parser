FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /code
WORKDIR /code
ADD ./requirements.txt .
RUN pip3 install -r requirements.txt