FROM python:3.12.9-slim
LABEL authors="wiky"
WORKDIR /app
COPY . /app
RUN apt install -y curl gdb
RUN pip3 install gunicorn
RUN pip3 install -r requirements.txt

#CMD ["gunicorn", "-w 3", "-b 0.0.0.0", "main:app"]
CMD ["python3", "/app/main.py"]
EXPOSE 5000