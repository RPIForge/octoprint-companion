#!/bin/bash

echo "starting key script"
exec /key.sh &

echo "starting octoprint"

sleep 10000
exec "/usr/local/bin/python /usr/local/bin/octoprint serve --iknowwhatimdoing --host 0.0.0.0 --port 5000 --basedir /octoprint/octoprint"


