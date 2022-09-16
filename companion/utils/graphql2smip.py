import os, argparse, json, requests
from datetime import datetime
import json
import pandas as pd
import config.smip as config  #copy config-example.py to config.py and set values
from utils.logging import logger


class graphql2smip():
    def __init__(self):
        
        #init variable object
        self.api_key = os.getenv('OCTOPRINT_KEY',"test")
        self.url = os.getenv('OCTOPRINT_URL',"http://octoprint:5000")
        
        tagid_actual= os.getenv('SMIP_TRMP_ACTUAL_TAG_ID',"24410")
        tagid_setpoint=os.getenv('SMIP_TRMP_SETPOINT_TAG_ID',"24413")
        self.tagid= [int(tagid_actual),int(tagid_setpoint)]
        
        self.authenticator=os.getenv('SMIP_AUTH',"ShuYang")
        self.pswd=os.getenv('SMIP_PSWD',"Admin123456")
        self.name=os.getenv('SMIP_ACCT',"yangs18")
        self.role=os.getenv('SMIP_ROLE',"rpi_ro_group")
        self.url=os.getenv('SMIP_URL',"https://rpi.cesmii.net/graphql")
        self.bearer_token=config.smip["bearer_token"]
        

    def do_split(self,full_df, column_no):
        df_new = full_df.iloc[:, [0, column_no]].copy()
        df_new['status'] = pd.Series([1 for x in range(len(df_new.index))])
        df_new = df_new.astype(str)

        return df_new


    def perform_graphql_request(self,content, headers=None):
        #print("Performing request with content: ")
        #print(content)

        r = requests.post(self.url, headers=headers, data={"query": content})
        r.raise_for_status()
        return r.json()


    def get_bearer_token(self):
        response = self.perform_graphql_request(f"""
        mutation authRequest {{
            authenticationRequest(
            input: {{authenticator: "{self.authenticator}", role: "{self.role}", userName: "{self.name}"}}
            ) {{
            jwtRequest {{
                challenge, message
            }}
            }}
        }}
        """)
        jwt_request = response['data']['authenticationRequest']['jwtRequest']
        if jwt_request['challenge'] is None:
            # raise requests.exceptions.HTTPError(jwt_request['message'])
            self.logger.error("bearer token authentification: " + jwt_request['message'])
        else:
            print("Challenge received: " + jwt_request['challenge'])
            response = self.perform_graphql_request(f"""
            mutation authValidation {{
                authenticationValidation(
                input: {{authenticator: "{self.authenticator}", signedChallenge: "{jwt_request["challenge"]}|{self.pswd}"}}
                ) {{
                jwtClaim
                }}
            }}
        """)
        
        jwt_request = {}
        if response:
            jwt_request = response.get("data",{}).get("authenticationValidation",{}).get("jwtClaim",{})
            # jwt_claim = response['data']['authenticationValidation']['jwtClaim']
        return f"Bearer {jwt_request}"


    def do_query(self,smp_query,logger):
        logger.info("Requesting Data from CESMII Smart Manufacturing Platform...")
        ''' Request some data -- this is an equipment query.
            Use Graphiql on your instance to experiment with additional queries
            Or find additional samples at https://github.com/cesmii/API/blob/main/Docs/queries.md '''
        smp_response = ""
        success=True
        logger.info("Requesting data with the current bearer token")
        try:
            #Try to request data with the current bearer token
            smp_response = self.perform_graphql_request(
                smp_query, headers={"Authorization": self.bearer_token})
        except requests.exceptions.HTTPError as e:
            # 403 Client Error: Forbidden for url: https://demo.cesmii.net/graphql
            #print(e)
            if "forbidden" in str(e).lower() or "unauthorized" in str(e).lower():
                logger.info("Bearer Token expired! Attempting to retreive a new GraphQL Bearer Token...")

                #Authenticate
                current_bearer_token = self.get_bearer_token()
                logger.info("New Token received: " + self.bearer_token)

                #Re-try our data request, using the updated bearer token
                logger.info("Re-try our data request, using the updated bearer token")
                smp_response = self.perform_graphql_request(
                    smp_query, headers={"Authorization": current_bearer_token})
            else:
                logger.error("An error occured accessing the SM Platform!")
                logger.error(e)
                success=False
                exit(-1)

        return smp_response,success


    def create_mutation_string(self,data_df,column_id, column_name, tagid, startTime, endTime):
        header = 'mutation { replaceTimeSeriesRange(input: {attributeOrTagId: "' + tagid + '" entries: '
        footer = ' startTime: "' + startTime + '" endTime: "' + endTime + '" } ) { clientMutationId json } }'
        split_df = self.do_split(data_df, column_id)
        split_df.rename(columns={column_name: 'value'}, inplace=True)
        mutation_data = split_df.to_json(orient='records', lines=False).replace(
            '"timestamp"',
            'timestamp').replace('"value"', 'value').replace('"status"', 'status')
        mutation_data.replace('"value"', 'value')
        mutation_string = "{}{}{}".format(header, mutation_data, footer)
        return mutation_string


    def create_query_string(self,tagid, startTime, endTime):
        query_string = '{ getRawHistoryDataWithSampling(maxSamples: 0, ids: ["'+ tagid + '"], startTime: "' +\
                        startTime +'",  endTime: "' + endTime + '"){ ts floatvalue} }'
        return query_string

    def write_smip(self,data_df,logger):
        logger.debug("******started uploading to smip")
        startTime=data_df.iloc[0,0]
        logger.debug("******start time is {} ".format(startTime))
        endTime=data_df.iloc[-1,0]
        logger.debug("******end time is {} ".format(endTime))
        column_name_list=(data_df.columns.values.tolist())[1:]
        
        
        
        for column_id in range(len(self.tagid)):
            logger.debug("******start uploading each column")
            column_name = column_name_list[column_id]
            logger.debug("******column_name is "+column_name)
            tagid = str(self.tagid[column_id])
            logger.debug("******tagid is {} ".format(tagid))
            
            logger.debug("******before mutation {} {} {}".format(column_name,startTime,endTime))
            mutation_string = self.create_mutation_string(data_df,column_id+1, column_name, tagid,
                                             startTime, endTime)
            logger.debug("******mutation string is{}".format(mutation_string))
            smp_response,success = self.do_query(str(mutation_string),logger)
            
            if not success:
                return success
            logger.debug("Response from SM Platform was...")
            logger.debug(json.dumps(smp_response, indent=2))
        return success
