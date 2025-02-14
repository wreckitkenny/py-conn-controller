FROM python:3.9.6-alpine
LABEL authors="wiky"
WORKDIR /app
COPY . /app
RUN apk add curl gdb
RUN pip3 install gunicorn
RUN pip3 install -r requirements.txt
CMD ["gunicorn", "-w 4", "-b 0.0.0.0", "main:app"]