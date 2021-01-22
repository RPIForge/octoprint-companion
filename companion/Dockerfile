FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /companion
ADD ./requirements.txt /companion/requirements.txt #move just the requirrements. This allows for caching of pip
RUN pip install -r requirements.txt
ADD . /companion/
CMD ["./wait-for-it", "octoprint:5000"] #wait for octoprint to start up
CMD ["python","main.py"] #ran when actually starting the container
