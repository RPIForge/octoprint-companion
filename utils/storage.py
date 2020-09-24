#for sys enviroment
import os

#s3 resource
import boto3

#postgres import
import psycopg2

#random string creation
import uuid


class postgres():
    #table information
    table = ""
    connection = None
    cursor = None
    
    variable = None
    logger = None
    def __init__(self, variable):
        self.variable = variable_class
        self.logger = self.variable.logger_class.logger
        
        #user information
        user = os.getenv('POSTGRES_USER',"")
        secret = os.getenv('POSTGRES_SECRET',"")
        
        #databse information
        database = os.getenv('POSTGRES_DB',"forge_octoprint")
        self.table = os.getenv('POSTGRES_TABLE',"")
        
        #server location
        ip = os.getenv('POSTGRES_IP',"192.168.1.10")
        port = os.getenv('POSTGRES_PORT',"5432")
        
        try:
            self.logger.info("Connecting to Postgres database: {}".format(database))
            self.connection = psycopg2.connect(
                host=ip,
                port=port,
                database=database,
                user=user,
                password=secret
            )
            self.cursor = self.connection.cursor()
        except:
            self.logger.error("Error connecting to Postgres database: {}".format(database))
        
        #set table name
        self.table = "print_table"
        
        #see if table exists
        self.cursor.execute("select exists(select * from information_schema.tables where table_name=%s)", (self.table,))
        if(not self.cursor.fetchone()[0]):
            #create table if it doesnt exist
            create_command = '''CREATE TABLE %s (
               job_id SERIAL PRIMARY KEY,
               printer_id integer,
               file VARCHAR(36),
               start_time timestamp,
               time_completed timestamp,
               finish_status VARCHAR(36),
               temperature_history text
               
            );'''
            
            self.cursor.execute(create_command, (self.table,))
        
    def create_row(self, dictionary):
        pass
        
    def update_row(self, row_id, dictionary):
        

class s3():
    s3_resource = None
    bucket = None
    
    variable = None
    logger = None
    def __init__(self, variable):
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
       
        
    
    
    
class storage():
    s3 = None
    postgresql = None
    
    
    variable = None
    logger = None
    def __init__(self,variable_class):
        self.variable = variable_class
        self.logger = self.variable.logger_class
        
        self.logger.info("Initalizing Storage Class")
        self.logger.info("Initializing s3 Class")
        self.s3 = s3()
        self.logger.info("Finished initializing s3 Class")
        
        self.logger.info("Initializing postgres Class")
        self.postgresql = postgres()
        self.logger.info("Finished initializing postgres Class")
    
    def start_print(self, file):
        #if job_id is none then finish
        
        #upload file and get uuid
        #create row in job table
        #set job_id in variable
        
    def finish_print(self):
        #update finished row
    
    def send_temperature(self, temperature):
        #update row
        
    
        
        
    

    
    
    