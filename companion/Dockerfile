FROM python:3.8
ENV PYTHONUNBUFFERED=1
WORKDIR /companion


RUN uname -a
RUN apt update
RUN apt install -y --fix-missing pkg-config
RUN apt install -y --fix-missing libhdf5-serial-dev libhdf5-dev python3-h5py
RUN apt install -y --fix-missing build-essential libssl-dev libffi-dev  cargo

RUN pip install --upgrade pip setuptools wheel

COPY ./requirements.txt /companion/
RUN pip install -r requirements.txt

COPY . /companion/
CMD ["flask","run","-h","0.0.0.0","-p","80"]
