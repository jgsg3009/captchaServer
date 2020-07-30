ARG TF_PACKAGE_VERSION
FROM tensorflow/tensorflow:latest-gpu

RUN apt-get update && apt-get install -y \
	build-essential \
	checkinstall \
	libreadline-gplv2-dev \
	libncursesw5-dev \
	libssl-dev \
	libsqlite3-dev \
	libgdbm-dev \
	libc6-dev \
	libbz2-dev \
	zlib1g-dev \
	openssl \
	libffi-dev 

WORKDIR /root/src

EXPOSE 5000
