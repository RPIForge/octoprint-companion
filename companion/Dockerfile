FROM python:3.8
ENV PYTHONUNBUFFERED=1
WORKDIR /companion


RUN uname -a
RUN apt update
RUN apt install -y --fix-missing pkg-config
RUN apt install -y --fix-missing libhdf5-serial-dev libhdf5-dev python3-h5py

RUN pip install --upgrade pip setuptools wheel

COPY ./requirements.txt /companion/
RUN pip install -r requirements.txt

COPY ./wait-for-it.sh /companion/wait-for-it.sh
RUN chmod +x /companion/wait-for-it.sh

COPY . /companion/
CMD ["/companion/wait-for-it.sh","octoprint:5000","--","flask","run","-b","0.0.0.0:8000"]
