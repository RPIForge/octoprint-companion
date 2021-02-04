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

##Disk Imports
#h5py
import h5py
import numpy

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

    

class disk_storage:
    #root_group
    file = None
    
    #default dataset size. Also the size to increment the resize
    buffer_size = 1000

    #used for traversal
    loc_data = None
    
    variable = None
    logger = None

    def __init__(self, variable_class):
        self.variable = variable_class
        self.logger = self.variable.logger_class.logger

        #get buffer location and size
        file_name = os.getenv("BUFFER_LOC","temp_read.hdf5")
        self.buffer_size = int(os.getenv("BUFFER_SIZE","1000"))
        
        mode = 'w'
        if(os.path.isfile(file_name)):
            mode='r+'

        #open file
        self.logger.info("opening h5py file")
        self.file = h5py.File(file_name,mode)
        
        #initialize loc_data
        self.loc_data = {}


        #if data already exists set loc to correct location
        if(len(list(self.file.keys())) != 0):
            self.logger.info("found previous datasets")
            for key in list(self.file.keys()):
                dset = self.file[key]
                if('loc' in dset.attrs):
                    self.loc_data[key] = dset.attrs['loc']
                else:
                    self.loc_data[key] = 0


    def push_data(self, data_name, array, width=4):
        #if key has not been created create new dset
        if(data_name not in list(self.file.keys())):
            self.logger.debug("creating dataset {}".format(data_name))
            dset = self.file.create_dataset(data_name, (self.buffer_size,width), maxshape=(None,width),dtype=h5py.string_dtype())
            
            dset.attrs['loc'] = 0
            self.loc_data[data_name] = 0
        else:
            dset = self.file[data_name]

        #if loc is bigger than available then resize dset
        loc = self.loc_data[data_name]
        if(loc >= dset.size):
            dset.resize((dset.size+self.buffer_size),width)

        #validate all data is string
        for index in range(len(array)):
            array[index] = str(array[index])

        #update data in array
        self.logger.debug("Pushing data {} to loc {} in dataset {}".format(array,loc,data_name))
        dset[loc] = array
        
        dset.attrs['loc'] = loc + 1
        self.loc_data[dset] = loc + 1
        
        #flush the h5py buffer to disk
        self.file.flush()

    #get data from one dset
    def get_data(self, dset):
        return self.file[dset][:self.loc_data[dset]]

    #get all of the data from the store
    def get_all_data(self):
        output_dict = {}

        #for all of the datasets gather there data
        for key in list(self.file.keys()):
            output_dict[key] = self.get_data(key)
        
        return output_dict
    
    #clear data for individual dset
    def clear_data(self,dset):
        #get dataset
        dset = self.file[key]
        shape = dset.shape
        width = shape[1]

        #first shrink the dataset to the original size and then overrite any leftover data
        numpy.resize(dset, (self.buffer_size,width))
        dset[:] = [b'']*width

        #reset the loc
        dset.attrs['loc'] = 0

    #clear the data from the datasets
    def clear_all_data(self):
        #for all datasets
        for key in list(self.file.keys()):
            self.clear_data(key) 
    




        
    
    
