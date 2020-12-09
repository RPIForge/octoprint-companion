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
    s3_bucket = None
    
    variable = None
    logger = None
    def __init__(self, variable_class):
        self.variable = variable_class
        self.logger = self.variable.logger_class.logger
        
        
        user = os.getenv('S3_USER',"user")
        secret = os.getenv('S3_SECRET',"123456789")
        ip = os.getenv('S3_IP',"192.168.1.10")
        port = os.getenv('S3_PORT',"8000")
        
        session = boto3.session.Session()
        
        try:
            self.logger.info("Connecting to s3 resource")


            self.s3_resource = session.resource(
                service_name="s3",
                aws_access_key_id=user,
                aws_secret_access_key=secret,
                config=boto3.session.Config(signature_version='s3v4', connect_timeout=5, retries={'max_attempts': 0}),
                endpoint_url='http://{}:{}'.format(ip,port),
            ) 
            
            bucket_name = '{}'.format(self.variable.name)
            self.s3_bucket = self.s3_resource.Bucket(name=bucket_name)
            
            if(self.s3_bucket not in self.s3_resource.buckets.all()):
                self.s3_bucket = self.s3_resource.create_bucket(Bucket=bucket_name)
                
        except Exception as ex:
            self.logger.error("Failed connecting to s3 resource")
            self.logger.error(ex)
        
        
        


    
    def upload_file(self, file):
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
        
       
        

        
    
        
        
    

    
    
    