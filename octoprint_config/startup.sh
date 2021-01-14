#!/bin/bash

KEY=$(cat /octoprint/octoprint/config.yaml | grep key| cut -d ":" -f2 | xargs)
echo "OCTOPRINT_KEY=$KEY">/config/octoprint.env


sleep 1000
exec "octoprint serve"
