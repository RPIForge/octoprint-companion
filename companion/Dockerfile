FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /companion
COPY ./requirements.txt /companion/
RUN pip install -r requirements.txt
COPY . /companion/
RUN chmod +x ./wait-for-it
CMD ["./wait-for-it", "octoprint:5000"] #wait for octoprint to start up
CMD ["python","main.py"] #ran when actually starting the container
