FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /companion

COPY ./requirements.txt /companion/
RUN pip install -r requirements.txt

COPY ./wait-for-it.sh /companion/wait-for-it.sh
RUN chmod +x /companion/wait-for-it.sh

COPY . /companion/
CMD ["/companion/wait-for-it.sh","octoprint:5000","--","python","main.py"]
