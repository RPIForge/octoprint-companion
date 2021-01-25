FROM octoprint/octoprint:latest 

COPY plugins.txt /plugins.txt
RUN python -m pip --disable-pip-version-check install  -r /plugins.txt 


COPY octoprint-config.yaml /octoprint/octoprint/config.yaml
COPY octoprint-users.yaml /octoprint/octoprint/users.yaml
