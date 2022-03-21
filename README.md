# octoprint-companion
This is the repo to store the code for the octoprint script. This script is intented to be run along side an octoprint instance. It can also send data to a endpoint and even upload files to a s3 resource. This can be configured via enviromental variables. To view more information about octoprint visit https://octoprint.org/

## Install

This repo has been set up using docker-compose. To build the docker image first run 

`docker-compose build`

Then start up just the octoprint instance by running 

`docker-compose run -d octoprint`

Then use the following command to get the container id. The container name should be something similar to `octoprint-companion_octoprint`

`docker ps`

Then take that container id and run the following command to get the octoprint API key that is stored in the container.

## Organization

This data collection system is split into two sections the companion and octoprint

### Octoprint
The octoprint container is based off of the [octoprint/octoprint](https://hub.docker.com/r/octoprint/octoprint) image with a custom config and users.

### Companion
The companion is a python application that will routinly call the octoprint api to get information and then upload that data to influxdb and the forge website. 
