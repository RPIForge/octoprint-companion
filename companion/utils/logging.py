#
# Logging File. File to initalize logger
#


#Impport to creater log folder if none exists
import os
import time
#Import logging classes
import sys
import logging


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, level):
       self.logger = logger
       self.level = level
       self.linebuf = ''

    def write(self, buf):
       for line in buf.rstrip().splitlines():
          self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass



class logger():
    variable_object = None
    logger = None
    
    def __init__(self, variable):
        #init variable object
        self.variable_object = variable

        if(not os.path.isdir("logs")):
            os.mkdir("logs")

        self.logger = logging.getLogger()
        
        level_var = os.getenv('LOG',"INFO")
        if(level_var == "DEBUG"):
            level = logging.DEBUG
        elif(level_var == "INFO"):
            level = logging.INFO
        elif(level_var == "WARN"):
            level = logging.WARN
        elif(level_var == "ERROR"):
            level = logging.ERROR
        else:
            level = logging.ERROR

        #Set logger levels
        self.logger.setLevel(level)
       
        # create file handler which logs all messages
        file_handler = logging.FileHandler('logs/general_logs.log', mode='a')
        file_handler.setLevel(level)

        # create console handler with a higher log level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # create formatter and add it to the handlers
        file_formatter = logging.Formatter('{"time":"%(asctime)s","logger_name":"%(name)s", "thread":"%(threadName)s","path":"%(pathname)s","line":"%(lineno)d","level":"%(levelname)s", "message":"%(message)s"}')
        file_handler.setFormatter(file_formatter)
        
        console_formatter = logging.Formatter('%(asctime)s %(threadName)s %(levelname)s [%(pathname)s:%(lineno)d] %(message)s')
        console_handler.setFormatter(console_formatter)
        
        #attach stdout and stderr to logger
        sys.stdout = StreamToLogger(self.logger,logging.INFO)
        sys.stderr = StreamToLogger(self.logger,logging.ERROR)

        #adder handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.logger.info("___________.__             ____________________.___  ___________")
        self.logger.info("\__    ___/|  |__   ____   \______   \______   \   | \_   _____/__________  ____   ____")
        self.logger.info("  |    |   |  |  \_/ __ \   |       _/|     ___/   |  |    __)/  _ \_  __ \/ ___\_/ __ \ ")
        self.logger.info("  |    |   |   Y  \  ___/   |    |   \|    |   |   |  |     \(  <_> )  | \/ /_/  >  ___/")
        self.logger.info("  |____|   |___|  /\___  >  |____|_  /|____|   |___|  \___  / \____/|__|  \___  / \___  >")
        self.logger.info("                \/     \/          \/                     \/             /_____/      \/")
