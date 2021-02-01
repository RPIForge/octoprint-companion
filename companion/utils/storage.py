#
# Storage File. This file handles storing files in s3
#

##General Imports
#for sys enviroment
import os

#random string creation
import uuid

##S3 Imports
#s3 resource
import boto3

##Influx Imports
#Influx Writers
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

class s3():
    s3_resource = None
    s3_bucket = None
    
    variable = None
    logger = None
    connected = False

    def __init__(self, variable_class):
        self.variable = variable_class
        self.logger = self.variable.logger_class.logger
        
        #get env variables 
        user = os.getenv('S3_USER',"")
        secret = os.getenv('S3_KEY',"")
        url = os.getenv('S3_URL',"http://127.0.0.1")
        port = os.getenv('S3_PORT',"8000")
        
        #create session
        session = boto3.session.Session()
        
        try:
            self.logger.info("Connecting to s3 resource")

            #create connection to s3 resource
            self.s3_resource = session.resource(
                service_name="s3",
                aws_access_key_id=user,
                aws_secret_access_key=secret,
                config=boto3.session.Config(signature_version='s3v4', connect_timeout=5, retries={'max_attempts': 0}),
                endpoint_url='{}:{}'.format(url,port),
            ) 
            
            #get bucket
            bucket_name = '{}'.format(self.variable.name)
            self.s3_bucket = self.s3_resource.Bucket(name=bucket_name)
            
            #if bucket isnt in s3 then create one
            if(self.s3_bucket not in self.s3_resource.buckets.all()):
                self.s3_bucket = self.s3_resource.create_bucket(Bucket=bucket_name)
                
            self.connected = True
        except Exception as ex:
            self.logger.error("Failed connecting to s3 resource")
            self.logger.error(ex)
            self.connected = False
        
        
        


    
    def upload_file(self, file):
        if(not self.connected):
            self.logger.info("S3 resource is not connected. Skipping upload")
            return ""
        
        object_name = str(uuid.uuid4())          
        try:
            #this is to save space and just return the hash of the previos upload
            current_hash = file.fileinfo['hash']
            for previous_upload in self.s3_bucket.objects.all():
                if(previous_upload.e_tag == "\""+str(current_hash)+"\""):
                    return previous_upload.key
                    
                
            
            self.s3_bucket.upload_file(file.name, object_name)
            self.logger.info("Successfully uploaded file")
            return object_name
        except Exception as ex:
            self.logger.error("Failed to upload file")
            self.logger.error(ex)
            return ""
        
       

class influx():
    #General
    influx_client = None
    influx_org = None
   
    #accessors
    influx_write = None
    influx_query = None
    

    #bucket names
    temperature_bucket = None
    location_bucket = None

    #general
    variable = None
    logger = None
    def __init__(self,variable_class):
        self.variable = variable_class
        self.logger = self.variable.logger_class.logger


        #get env variables
        host = os.getenv('INFLUX_URL',"http://influx")
        port = os.getenv('INFLUX_PORT',"8086")
        token = os.getenv('INFLUX_TOKEN',"")
        self.influx_org = os.getenv('INFLUX_ORG',"forge")

        

        #connect to influx
        self.logger.info("Connecting to InfluxDB")
        self.influx_client = InfluxDBClient(url=host+":"+str(port), token=token)
        self.influx_write = self.influx_client.write_api(write_options=SYNCHRONOUS)
        self.influx_query = self.influx_client.query_api()

        #get bucket information
        self.temperature_bucket = os.getenv('TEMPERATURE_BUCKET',"temperature_data")
        self.location_bucket = os.getenv('LOCATION_BUCKET',"location_data")
        

    def generate_tags(self):
        tag_list = []
        tag_list.append(('machine_name',self.variable.name))
        tag_list.append(('machine_type',self.variable.type))
        tag_list.append(('machine_id',self.variable.printer_id))

        if(self.variable.job is not None and self.variable.job_id is not None):
            tag_list.append(('job',self.variable.job))
            tag_list.append(('job_id',self.variable.job_id))
        
        return tag_list

    def write(self, name, bucket, time, tags, fields):
        self.logger.debug("writting to influxdb")
        
        #create data_point
        data_point = Point(name)
        
        #set time
        data_point.time(time)

        #assign tags
        for tag in tags:
            data_point.tag(tag[0], str(tag[1]))
        
        for field in fields:
            data_point.field(field[0], float(field[1]))
        
        try:
            self.influx_write.write(bucket, self.influx_org, data_point)
            self.logger.debug("Successfully wrote to influx bucket {}".format(bucket))
            return True
        except Exception as e:
            self.logger.error("Unable to write to influx bucket {}".format(bucket))
            self.logger.error(e)
            return False

    


        
        
    

    
    
    
