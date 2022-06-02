# octoprint-companion
This is the repo to store the code for the octoprint script. This script is intented to be run along side an octoprint instance. It can also send data to a endpoint and even upload files to a s3 resource. This can be configured via enviromental variables. To view more information about octoprint visit https://octoprint.org/

## Install

This repo has been set up using docker-compose. To build the docker images first run 

`docker-compose build`

Then start up an instance of octoprint, influx, and the python agent by running the following docker command

`docker-compose up -d`

### Testing

In testing the application the following endpoints are useful in monitoring data.

| Name      | Endpoint             | Notes                            |
|-----------|----------------------|----------------------------------|
| MTConnect | localhost:80/current |                                  |
| Octoprint | localhost:5000       | default account is: pi, rpiforge |
| OCP UA    | localhost:4840       |                                  |
| InfluxDB  | localhost:8086       |                                  |

It is also useful to use the (Octoprint Virtual Printer)[https://docs.octoprint.org/en/master/development/virtual_printer.html] to test without having to hook up to a machine.

## Architecture

## This Repo
This data collection system is split into two sections the companion and octoprint

### Octoprint
The octoprint container is based off of the [octoprint/octoprint](https://hub.docker.com/r/octoprint/octoprint) image with a custom config and users.

### Companion
The companion is a python application that will routinly call the octoprint api to get information and then upload that data to influxdb and the forge website. It also makes this data aviable via MTConnect endpoints for open access. 

## Dependencies
This system depends on influxdb to store all of the historic time series data. This system can also interact with the [rpiforge website](https://github.com/RPIForge/website) to get its current information.
