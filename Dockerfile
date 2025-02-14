FROM python:3.12.9-alpine
LABEL authors="wiky"
WORKDIR /app
COPY . /app
RUN apk add curl gdb
RUN pip3 install gunicorn
RUN pip3 install -r requirements.txt

EXPOSE 8000
CMD ["gunicorn", "-w 3", "-b 0.0.0.0", "main:app"]
#CMD ["python3", "/app/main.py"]