FROM python:3.12.9-alpine
LABEL authors="wiky"
WORKDIR /app
COPY . /app
RUN apk add curl gdb
RUN pip3 install -r requirements.txt
EXPOSE 5000
CMD ["python3", "/app/main.py"]
