FROM octoprint/octoprint:latest 

ENV PIP_USER true
ENV PYTHONUSERBASE /octoprint/plugins
ENV PATH "${PYTHONUSERBASE}/bin:${PATH}"


ENV PIP_USER false
COPY plugins_list.txt /plugins_list.txt
RUN pip install -r /plugins_list.txt
ENV PIP_USER true


COPY octoprint-config.yaml /octoprint/octoprint/config.yaml
COPY octoprint-users.yaml /octoprint/octoprint/users.yaml
