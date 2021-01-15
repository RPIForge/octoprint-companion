FROM octoprint/octoprint:latest 
COPY startup.sh /startup.sh
COPY plugins.txt /plugins.txt
COPY octoprint-config.yaml /octoprint/octoprint/config.yaml
COPY octoprint-users.yaml /octoprint/octoprint/users.yaml
RUN pip install -r /plugins.txt 
