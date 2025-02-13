FROM python:3.9.6-alpine
LABEL authors="wiky"
WORKDIR /app

COPY . /app

RUN pip3 install gunicorn

RUN pip3 install -r requirements.txt

ENTRYPOINT ["gunicorn", "-w 4", "-b 0.0.0.0", "main:app"]