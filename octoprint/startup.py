#this file generates an API key to octoprints standards and then sets its value
import os
import uuid
from builtins import bytes

#function to generate key
def generate_api_key():
    return "".join("%20X" % z for z in bytes(uuid.uuid4().bytes))


#generate api key
api_key = generate_api_key()
            
#set octoprint api key
os.system('octoprint config set api.key "{}"'.format(api_key))

os.mkdir('/config/')

#get the  config file
file_name = os.getenv("ENV_FILE","/config/octoprint.env")

#write key to file
output_file = open(file_name, 'w')
output_file.write("OCTOPRINT_KEY={}".format(api_key))
output_file.close()

