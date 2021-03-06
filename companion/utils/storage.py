#
# Storage File. This file handles storing files in s3
#

##General Imports
#for sys enviroment
import os
import threading 

#random string creation
import uuid

##S3 Imports
#s3 resource
import boto3

##Influx Imports
#Influx Writers
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import ASYNCHRONOUS

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
        url = os.getenv('S3_URL',"http://127.0.0.1:9000")

        
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
                endpoint_url=url,
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
        
        
        

    def connected(self):
        return self.connected
    
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
        url = os.getenv('INFLUX_URL',"http://influx:8086")
        token = os.getenv('INFLUX_KEY',"")
        self.influx_org = os.getenv('INFLUX_ORG',"forge")

        

        #connect to influx
        self.logger.info("Connecting to InfluxDB")
        self.influx_client = InfluxDBClient(url=url, token=token)
        self.influx_write = self.influx_client.write_api(write_options=ASYNCHRONOUS)
        self.influx_query = self.influx_client.query_api()


    def generate_tags(self):
        tag_list = {}
        tag_list['machine_name'] = self.variable.name
        tag_list['machine_type'] = self.variable.type
        tag_list['machine_id'] = self.variable.printer_id

        return tag_list

    def generate_point(self, name, time, tags, fields):
        #update new tags wiht generic tags
        tags.update(self.generate_tags())
        
        #create data_point
        data_point = Point(name)
        
        #set time
        data_point.time(time)

        #assign tags
        for key in tags:
            data_point.tag(key, str(tags[key]))
        
        for key in fields:
            data_point.field(key, fields[key])

        
        #if datapoint is empty
        if(data_point._fields == {}):
            return None

        return data_point
    
    def write_point(self,bucket,point):
        return self.write_points(bucket,[point])

    #write either individual point or points
    def write_points(self,bucket,point_array):
        if(point_array == []):
            self.logger.debug("no data to write to influx")
            return True
        

        self.logger.debug("writting to influxdb")
         
        try:
            self.influx_write.write(bucket, self.influx_org, point_array)
            self.logger.debug("Successfully wrote {} datapoints to influx bucket {}".format(len(point_array),bucket))
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

    #data lock - lock db when updating influx and when pushing data.
    # Currently this lock is taken in push_data and in task
    lock = False
    lock_name = ''

    variable = None
    logger = None

    def __init__(self, variable_class):
        self.variable = variable_class
        self.logger = self.variable.logger_class.logger

        #get buffer location and size
        file_name = os.getenv("BUFFER_LOC","temp_read.hdf5")
        self.buffer_size = int(os.getenv("BUFFER_SIZE","1000"))
        
        #initialize loc_data
        self.loc_data = {}

        
        #open file
        #if files exists move it to .backup and open it as readonly. Then duplicate the contents to thecorrect file
        # This handles bad written data at the end of the previous crash. This is not a great solution but the one
        # h5py have provided for now

        
        if(os.path.isfile(file_name)):
            self.logger.info("Handling previous data")

            #move file to backup
            old_file_name = file_name+'.old'
            os.rename(file_name,old_file_name)
            
            #open old and new file
            try:
                old_file = h5py.File(old_file_name,'r',swmr=True, libver='latest')
                self.file = h5py.File(file_name,'w', libver='latest')
                self.file.swmr_mode = True

                #for old datasets copy data
                for key in list(old_file.keys()):
                    old_file.copy(key,self.file)
                
                #close and delete old data
                old_file.close()
                os.remove(old_file_name)
            except Exception as e:
                self.logger.error("Handling previous data failed")
                self.logger.error(e)

        if(not self.file):
            self.logger.info("opening h5py file")
            self.file = h5py.File(file_name, 'w', libver='latest')
            self.file.swmr_mode = True


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
        self.acquire_lock(data_name)

        #if key has not been created create new dset
        if(data_name not in list(self.file.keys())):
            self.logger.debug("creating dataset {}".format(data_name))
            dset = self.file.create_dataset(data_name, (self.buffer_size,width), maxshape=(None,width),dtype=h5py.string_dtype())
            
            dset.attrs['loc'] = 0
            self.loc_data[data_name] = 0
        else:
            dset = self.file[data_name]
        
        self.logger.debug("Getting location for {}".format(data_name))
        #if loc is bigger than available then resize dset
        loc = self.loc_data[data_name]
        if(loc >= dset.size):
            dset.resize((dset.size+self.buffer_size),width)

        self.logger.debug("Validating data for {}".format(data_name))
        #validate all data is string
        for index in range(len(array)):
            array[index] = str(array[index])

        #update data in array
        self.logger.debug("Pushing data {} to loc {} in dataset {}".format(array,loc,data_name))
        dset[loc] = array
        
        dset.attrs['loc'] = loc + 1
        self.loc_data[data_name] = loc + 1
         
        self.logger.debug("Flushing data {} for disk".format(data_name))
        #flush the h5py buffer to disk
        self.file.flush()

        self.release_lock(data_name)

    #get data from one dset
    def get_data(self, dset_name, count=None):
        
        if(dset_name not in list(self.file.keys())):
            return []
        
        if(count is None):
            count = self.loc_data[dset_name]

        if(count > self.loc_data[dset_name]):
            count = self.loc_data[dset_name]
        
        if(count<0):
            count = self.loc_data[dset_name]+count

        return self.file[dset_name][:count]

    #get all of the data from the store
    def get_all_data(self):
        output_dict = {}

        #for all of the datasets gather there data
        for key in list(self.file.keys()):
            output_dict[key] = self.get_data(key)
        
        return output_dict
    
    #clear data for individual dset
    def clear_data(self,dset_name):
        self.logger.debug('clearing data from {}'.format(dset_name))
        if(dset_name not in list(self.file.keys())):
            return 
        
        #get dataset
        dset = self.file[dset_name]
        shape = dset.shape
        depth = shape[0]
       
        #reshrink buffer if its grown
        if(depth != self.buffer_size):
            self.logger.debug('resize buffer')
            numpy.resize(dset, (self.buffer_size,width))
    
        #reset the loc
        dset.attrs['loc'] = 0
        self.loc_data[dset_name] = 0

        self.file.flush()
        
        self.logger.debug('successfully cleared data from {}'.format(dset_name))

    #clear the data from the datasets
    def clear_all_data(self):
        #for all datasets
        for key in list(self.file.keys()):
            self.clear_data(key) 
    
    def acquire_lock(self, name):
        self.logger.debug("{} acquiring database lock".format(name))
        while(self.lock):
            pass
        self.lock = True
        self.lock_name = name
        self.logger.debug("{} database lock acquired".format(name))
    
    def release_lock(self, name):
        self.logger.debug("{} releasing database lock".format(name))
        self.lock_name = ''
        self.lock = False



        
    
    
