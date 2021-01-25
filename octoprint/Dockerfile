FROM octoprint/octoprint:latest 

COPY plugins.json /plugins.json
#RUN python -m pip --disable-pip-version-check install  -r /plugins.txt 

COPY add_plugins.py /add_plugins.py
RUN python /add_plugins.py

COPY octoprint-config.yaml /octoprint/octoprint/config.yaml
COPY octoprint-users.yaml /octoprint/octoprint/users.yaml
