FROM tensorflow/tensorflow:2.2.2-gpu

WORKDIR /root/src
COPY requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 5000
