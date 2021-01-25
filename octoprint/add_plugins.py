import json
import os


with open('/octoprint/octoprint/data/pluginmanager/plugins.json') as f1:
    data = json.load(f1)

with open('/plugins.json') as f2:
    extra_plugins = json.load(f2)


data = data + extra_plugins

with open('/octoprint/octoprint/data/pluginmanager/plugins.json', 'w') as f1:
    json.dump(data,f1)

