ARG TF_PACKAGE_VERSION
FROM tensorflow/tensorflow:latest-gpu

WORKDIR /root/src

EXPOSE 5000
