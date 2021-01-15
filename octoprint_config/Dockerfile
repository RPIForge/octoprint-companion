FROM octoprint/octoprint:latest 
COPY startup.sh /startup.sh
COPY plugins.txt /plugins.txt
RUN pip install -r /plugins.txt 
