FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY ./ /code/
RUN pip install -r /code/requirements.txt
CMD ["./wait-for-it", "octoprint:5000"] #wait for octoprint to start up
CMD ["python","main.py"] #ran when actually starting the container
