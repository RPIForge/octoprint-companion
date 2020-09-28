#for sys enviroment
import os

#s3 resource
import boto3

#postgres import
import psycopg2
from psycopg2 import sql

#random string creation
import uuid

#current time 
import datetime


class postgres():
    #table information
    table = ""
    connection = None
    
    variable = None
    logger = None
    
    
    #function to create/update commands.
    #Auto commits and closes curosr
    def execute_create(self, command, args):
        cursor = self.connection.cursor()
        cursor.execute(command,args)
        
        #get result for cursor
        try:
            result = cursor.fetchone()[0]
        except:
            result = None
            
            
        #close cursor
        cursor.close()
        # commit the changes
        self.connection.commit()
        
        #return result if present
        return result
    
    #function to get data from postgres
    #does not close cursor
    def execute_get(self, command, args):
        cursor = self.connection.cursor()
        cursor.execute(command,args)
        return cursor
        
    
    def __init__(self, variable_class):
        self.variable = variable_class
        self.logger = self.variable.logger_class.logger
        
        #user information
        user = os.getenv('POSTGRES_USER',"postgres")
        secret = os.getenv('POSTGRES_SECRET',"password")
        
        #databse information
        database = os.getenv('POSTGRES_DB',"forge_octoprint")
        self.table =  os.getenv('POSTGRES_TABLE',"print_table") 
        
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
            
        except:
            self.logger.error("Error connecting to Postgres database: {}".format(database))
            return None
        
        #set table name
        
        
        #see if table exists
        exists_cursor = self.execute_get("select exists(select * from information_schema.tables where table_name=%s)", (self.table,))
        exists = exists_cursor.fetchone()[0]
        exists_cursor.close()
        if(not exists):
            #create table if it doesnt exist
            create_text = '''CREATE TABLE {} (
               job_id SERIAL PRIMARY KEY,
               printer_id integer,
               file VARCHAR(36),
               start_time timestamp,
               time_completed timestamp,
               finish_status VARCHAR(36),
               temperature_history text
            );'''
            
            create_command = sql.SQL(create_text).format(sql.Identifier(self.table))
            
            self.execute_create(create_command)
        
        
    def create_row(self, file):
        row_text = '''
        INSERT INTO {} (printer_id, file,
        start_time, time_completed,
        finish_status,  temperature_history)
        VALUES (%s, %s, %s, %s, %s, %s) 
        RETURNING job_id;'''
        
        row_command = sql.SQL(row_text).format(sql.Identifier(self.table))
        
        
        row_variables = (self.variable.printer_id, 
                        file, datetime.datetime.utcnow(), None,
                        None, None)
        
        return self.execute_create(row_command,row_variables)
        
    def update_row(self, row_id, dictionary):
        output_text = ''
        for key in dictionary:
            output_text = output_text+" "+key+"="+str(dictionary[key])+","
        output_text = output_text[:-1]
        
        row_text = '''UPDATE {} SET %s WHERE job_id = %s;'''
        row_command = sql.SQL(row_text).format(sql.Identifier(self.table))
        
        return self.execute_create(row_command,(output_text,row_id,))
    
    def get_row(self, row_id):
        row_text = ''' select * from {}
        WHERE job_id = %s;'''
        row_command = sql.SQL(row_text).format(sql.Identifier(self.table))
        
        cursor = self.execute_get(row_command, (row_id,))
        try:
            result = cursor.fetchone()
        except:
            self.logger.debug("No data found matching row")

            result = None
        
        cursor.close()
        return result

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
       
        
    
    
    
class storage():
    s3 = None
    postgresql = None
    
    
    variable = None
    logger = None
    def __init__(self,variable_class):
        self.variable = variable_class
        self.logger = self.variable.logger_class.logger
        
        self.logger.info("Initalizing Storage Class")
        self.logger.info("Initializing s3 Class")
        self.s3 = s3(variable_class)
        self.logger.info("Finished initializing s3 Class")
        
        self.logger.info("Initializing postgres Class")
        self.postgresql = postgres(variable_class)
        self.logger.info("Finished initializing postgres Class")
    
    def start_print(self, file):
        if(job_id is not None):
            self.logger.warn("Past job was not finished")
            self.finish_print("Companion Error")
        
        #upload file and get uuid
        uuid = self.s3.upload_file(file)
        
        #create row in job table
        job_id = self.postgresql.create_row(uuid)
        
        #set job_id in variable
        self.variable.job_id = job_id
        
    def finish_print(self, status):
        self.postgresql.update_row(self.variable.job_id, {"finish_status":status,"time_completed":datetime.datetime.utcnow()})
        self.variable.job_id = None
    
    def send_temperature(self, temperature):
        if(self.variable.job_id is None):
            self.logger.warn("No current job for temperature")
            return None
        #update row
        result = self.postgresql.get_row(self.variable.job_id)
        
        if(result is None):
            self.logger.warn("No row with job_id for temperature")
            return None
            
        temperature_history = result[6]
        new_temperature_history = "{}:{},{}".format(temperature_history, datetime.datetime.utcnow(), temperature)
        self.postgresql.update_row(self.variable.job_id, {"temperature_history":new_temperature_history})
        
        
        
        pass
        
    
        
        
    

    
    
    