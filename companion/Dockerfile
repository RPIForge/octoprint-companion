FROM python:3.8
ENV PYTHONUNBUFFERED=1
WORKDIR /companion


RUN uname -a
RUN apt update
RUN apt install -y --fix-missing pkg-config
RUN apt install -y --fix-missing libhdf5-serial-dev libhdf5-dev python3-h5py

RUN pip install pip setuptools wheel

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
COPY ./requirements.txt /companion/
RUN pip install -r requirements.txt

COPY . /companion/
CMD ["flask","run","-h","0.0.0.0","-p","80"]
