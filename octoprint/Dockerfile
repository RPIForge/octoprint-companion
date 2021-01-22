FROM octoprint/octoprint:latest 

COPY plugins.txt /plugins.txt
RUN /usr/local/bin/python -m pip --disable-pip-version-check install  -r /plugins.txt --no-cache-dir

COPY octoprint-config.yaml /octoprint/octoprint/config.yaml
COPY octoprint-users.yaml /octoprint/octoprint/users.yaml
COPY startup.py /startup.py
RUN ["python", "/startup.py"]


#ENTRYPOINT ["/startup.sh"] #ran on container startup

