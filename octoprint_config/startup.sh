#!/bin/bash
echo "getting key"

KEY=$(cat /octoprint/octoprint/config.yaml | grep key| cut -d ":" -f2 | xargs)
echo "OCTOPRINT_KEY=$KEY">/config/octoprint.env

sleep 1000
exec "/usr/local/bin/python /usr/local/bin/octoprint serve --iknowwhatimdoing --host 0.0.0.0 --port 5000 --basedir /octoprint/octoprint"
