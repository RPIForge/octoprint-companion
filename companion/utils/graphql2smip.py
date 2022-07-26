import os, argparse, json, requests
from datetime import datetime
import json
import pandas as pd
import config.smip as config  #copy config-example.py to config.py and set values



class graphql2smip():
    def __init__(self,variable):
        self.tagid =config.smip["tagids"]
        self.authenticator=config.smip["authenticator"]
        self.pswd=config.smip["password"]
        self.name=config.smip["name"]
        self.role=config.smip["role"]
        self.url=config.smip["url"]
        self.bearer_token=config.smip["bearer_token"]
        self.variable=variable

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
            raise requests.exceptions.HTTPError(jwt_request['message'])
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
        jwt_claim = response['data']['authenticationValidation']['jwtClaim']
        return f"Bearer {jwt_claim}"


    def do_query(self,smp_query):
        self.variable.logger_class.logger.info("Requesting Data from CESMII Smart Manufacturing Platform...")
        ''' Request some data -- this is an equipment query.
            Use Graphiql on your instance to experiment with additional queries
            Or find additional samples at https://github.com/cesmii/API/blob/main/Docs/queries.md '''
        smp_response = ""
        success=True
        self.variable.logger_class.logger.info("Requesting data with the current bearer token")
        try:
            #Try to request data with the current bearer token
            smp_response = self.perform_graphql_request(
                smp_query, headers={"Authorization": self.bearer_token})
        except requests.exceptions.HTTPError as e:
            # 403 Client Error: Forbidden for url: https://demo.cesmii.net/graphql
            #print(e)
            if "forbidden" in str(e).lower() or "unauthorized" in str(e).lower():
                self.variable.logger_class.logger.info("Bearer Token expired! Attempting to retreive a new GraphQL Bearer Token...")

                #Authenticate
                current_bearer_token = self.get_bearer_token()
                self.variable.logger_class.logger.info("New Token received: " + self.bearer_token)

                #Re-try our data request, using the updated bearer token
                self.variable.logger_class.logger.info("Re-try our data request, using the updated bearer token")
                smp_response = self.perform_graphql_request(
                    smp_query, headers={"Authorization": current_bearer_token})
            else:
                self.variable.logger_class.logger.error("An error occured accessing the SM Platform!")
                self.variable.logger_class.logger.error(e)
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

    def write_smip(self,data_df):
        self.variable.logger_class.logger.debug("******started uploading to smip")
        startTime=data_df.iloc[0,0]
        self.variable.logger_class.logger.debug("******start time is {} ".format(startTime))
        endTime=data_df.iloc[-1,0]
        self.variable.logger_class.logger.debug("******end time is {} ".format(endTime))
        column_name_list=(data_df.columns.values.tolist())[1:]
        
        
        
        for column_id in range(len(self.tagid)):
            self.variable.logger_class.logger.debug("******start uploading each column")
            column_name = column_name_list[column_id]
            self.variable.logger_class.logger.debug("******column_name is "+column_name)
            tagid = str(self.tagid[column_id])
            self.variable.logger_class.logger.debug("******tagid is {} ".format(tagid))
            
            self.variable.logger_class.logger.debug("******before mutation {} {} {}".format(column_name,startTime,endTime))
            mutation_string = self.create_mutation_string(data_df,column_id+1, column_name, tagid,
                                             startTime, endTime)
            self.variable.logger_class.logger.debug("******mutation string is{}".format(mutation_string))
            smp_response,success = self.do_query(str(mutation_string))
            
            if not success:
                return success
            self.variable.logger_class.logger.debug("Response from SM Platform was...")
            self.variable.logger_class.logger.debug(json.dumps(smp_response, indent=2))
        return success

if __name__ == '__main__':
    # reading csv file
    data_file = 'steel_data.csv'
    data_df = pd.read_csv(data_file)
    data_df = data_df.astype(str)
    print(data_df)
    print(data_df.dtypes)
    
    
    data_uploader=graphql2smip()
    data_uploader.write_smip(data_df)
    print(123)