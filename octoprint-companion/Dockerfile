FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
CMD ["./wait-for-it", "octoprint:5000"] #wait for octoprint to start up
CMD ["python","main.py"] #ran when actually starting the container
