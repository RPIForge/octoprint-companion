#for sys enviroment
import os

#s3 resource
import boto3

#random string creation
import uuid

#current time 
import datetime

class s3():
    s3_resource = None
    bucket = None
    
    variable = None
    logger = None
    def __init__(self, variable_class):
        self.variable = variable_class
        self.logger = self.variable.logger_class.logger
        
        
        user = os.getenv('S3_USER',"")
        secret = os.getenv('S3_SECRET',"")
        ip = os.getenv('S3_IP',"192.168.1.10")
        port = os.getenv('S3_PORT',"8000")
        
        session = boto3.session.Session()
        
        try:
            self.logger.info("Connecting to s3 resource")
            self.s3_resource = session.resource(
                service_name="s3",
                aws_access_key_id=user,
                aws_secret_access_key=secret,
                endpoint_url='http://{}:{}'.format(ip,port),
            ) 
        except:
            self.logger.error("Failed connecting to s3 resource")
        
        self.bucket = self.variable.name
        


    
    def upload_file(self, file):
        object_name = str(uuid.uuid4())          
        self.s3_resource.meta.client.upload_file(file, self.bucket, object_name)
        return object_name
       
        

        
    
        
        
    

    
    
    