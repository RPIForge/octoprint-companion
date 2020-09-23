#for sys enviroment
import os

#s3 resource
import boto3

#random string creation
import uuid


class postgres():
    def __init__(self):
        pass

class s3():
    s3_resource = None
    
    variable = None
    
    def __init__(self):
        #init variable object
        user = os.getenv('S3_USER',"")
        secret = os.getenv('S3_SECRET',"")
        ip = os.getenv('S3_IP',"192.168.1.10")
        port = os.getenv('S3_PORT',"8000")
        
        session = boto3.session.Session()
        self.s3_resource = session.resource(
            service_name="s3",
            aws_access_key_id=user,
            aws_secret_access_key=secret,
            endpoint_url='http://{}:{}'.format(ip,port),
        )        
        
        self.variable = variable_class


    
    def upload_file(self, file):
        object_name = str(uuid.uuid4())          
        self.s3_resource.meta.client.upload_file(file, self.variable.name, object_name)
        return object_name
       
        
    
    
    
class storage():
    s3 = None
    postgresql = None
    
    
    variable = None
    def __init__(self,variable_class):
        self.variable = variable_class
        
        self.variable.logger_class.logger.info("Initalizing Storage Class")
        self.variable.logger_class.logger.info("Connecting to s3 service")
        self.s3 = s3()
        self.variable.logger_class.logger.info("Finished Connecting to s3 service")
        
        self.variable.logger_class.logger.info("Connecting to postgres service")
        self.postgresql = postgres()
        self.variable.logger_class.logger.info("Finished Connecting to postgres service")
        
    

    
    
    