FROM tensorflow/tensorflow:latest-gpu

WORKDIR /root/src

COPY entrypoint.sh .
COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 5000
