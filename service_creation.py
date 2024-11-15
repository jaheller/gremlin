import pandas as pd
import requests
import argparse
import json
import urllib.parse

## Goal is to read in a CSV file that contains details about a service we want to create or update
## This example assumes we have 3 health checks that we want to attach to each service a CPU load check,
## a network latency check, and a reachability "up" check.  In the CSV if the health check or service doesn't
## exist we also write back to it the ID if able to create those.

###############################################################################
## Check if a team exists, and create it if not (WIP)
###############################################################################
#def check_and_create_team(teamName, authToken):
#    url = "https://api.gremlin.com/v1/teams"
#    headers = {
#        "Authorization": f"{AUTHTYPE} {authToken}",
#        "Content-Type": "application/json"
#    }
#    response = requests.get(url, headers=headers)
#    if response.status_code == 200:
#        teams = response.json()
#        for team in teams:
#            if team['name'] == teamName:
#                print(f"Team {teamName} already exists.")
#                return team['id']
#    # Create team if it doesn't exist
#    print(f"Creating team: {teamName}")
#    payload = {"name": teamName}
#    response = requests.post(url, headers=headers, json=payload)
#    if response.status_code == 201:
#        print(f"Team created: {response.json()}")
#        return response.json()['id']
#    else:
#        print(f"Failed to create team: {response.text}")
#        return None


###############################################################################
## Create a new service
##  teamId = The specific team that contains the service
##  authToken = The API auth token to use passed as a parameter via env variable
##  jsonPayload = The service details from a CSV
###############################################################################
def create_service(teamId, authToken, jsonPayload):
    
    url = f"https://api.gremlin.com/v1/services?teamId={teamId}"
    
    headers = {
        "Authorization": f"{AUTHTYPE} {authToken}",
        "Content-Type": "application/json"
    }
    
    printDebug(f"Making API call to URL: {url}")
    response = requests.post(url, headers=headers, json=jsonPayload)
    
    printDebug(f"Response status code: {response.status_code}")
    printDebug(f"Response headers: {response.headers}")

    if response.status_code == 200:
        print(f"Service created {response.text}")
        return str(response.text)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


###############################################################################
## Create an external authentication to use for health checks
##  teamId = The specific team that contains the service
##  authToken = The API auth token to use passed as a parameter via env variable
##  jsonPayload = The auth details from a CSV
###############################################################################
def create_authentication(teamId, authToken, jsonPayload):
    
    url = f"https://api.gremlin.com/v1/external-integrations/status-check?observabilityToolType=CUSTOM&teamId={teamId}"
    
    headers = {
        "Authorization": f"{AUTHTYPE} {authToken}",
        "Content-Type": "application/json"
    }
    
    printDebug("Making API call to URL: {url}")
    response = requests.post(url, headers=headers, json=jsonPayload)
    
    printDebug(f"Response status code: {response.status_code}")
    printDebug(f"Response headers: {response.headers}")

    if response.status_code == 200:
        print("Authentication created")
        return str(response.text)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


###############################################################################
## Create an external authentication to use for health checks
##  teamId = The specific team that contains the service
##  authToken = The API auth token to use passed as a parameter via env variable
##  jsonPayload = The auth details from a CSV
###############################################################################
def create_healthcheck(teamId, authToken, jsonPayload):
    
    url = f"https://api.gremlin.com/v1/status-checks?teamId={teamId}"
    
    headers = {
        "Authorization": f"{AUTHTYPE} {authToken}",
        "Content-Type": "application/json"
    }
    
    printDebug(f"Making API call to URL: {url}")
    response = requests.post(url, headers=headers, json=jsonPayload)
    printDebug(f"Response status code: {response.status_code}")
    printDebug(f"Response headers: {response.headers}")

    if response.status_code == 201:
        print(f"Healthcheck created {response.text}")
        return str(response.text)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


###############################################################################
## Fetch details about the service
##  teamId = The specific team that contains the service
##  authToken = The API auth token to use passed as a parameter via env variable
##  serviceId = To select a specific service instead of all
###############################################################################
def fetch_services(teamId, authToken, serviceId = None):
    base_url = "https://api.gremlin.com/v1/"
    if serviceId:
        url = f"{base_url}services/{serviceId}?{teamId}"
    else:
        url = f"{base_url}services?teamId={teamId}"
    
    headers = {
               "Authorization": f"{AUTHTYPE} {authToken}",  # Use the token provided via command line
        "Content-Type": "application/json"
    }

    printDebug(f"Making API call to URL: {url}")
    response = requests.get(url, headers=headers)
    
    printDebug(f"Response status code: {response.status_code}")
    printDebug(f"Response headers: {response.headers}")
    ##printDebug(f"Response text: {response.text}")

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


###############################################################################
## Read in the CSV file and kick off the service creation
##  csvFile = The csv with the header line 1:
##  serviceName,serviceId,teamId,k8sName,namespace,kind,clusterId,authName,authUrl,healthNameCpu,serviceIdCpu,healthNameLatency,serviceIdLatency,healthNameUp,serviceIdNetwork
## Example data
## provisioning-engine,,55f67673-2ed3-4f60-c9c3-832ed3bf800d,opentelemetry-demo-paymentservice,otel-demo,DEPLOYMENT,cluster-58eaed5f,Google_AUTH,https://www.google.com,provisioning-engineCPUhealthCheck,,provisioning-engineLatencyHealthCheck,,provisioning-engineUphealthCheck,
##  authToken = The API auth token to use passed as a parameter via env variable
###############################################################################
def execute_API(csvFile, authToken, apiType):
    printDebug(f"Reading CSV file from path: {csvFile}")
    
    df = pd.read_csv(csvFile, na_filter= False)
    
    printDebug(f"CSV file loaded. Number of rows: {len(df)}")

    ## (WIP)
    #if apiType == "team":
    #    for index, row in df.iterrows():
    #        printDebug(f"Processing row {index + 1}")
    #        teamName = row['teamName']
    #        if not row['teamId'] or row['teamId'] == "None":
    #            response_data = check_and_create_team(teamName, authToken)
    #            #Grab the response data which is the service ID and write that to the CSV
    #            df.at[index, 'teamId'] = str(response_data)
    #            df.to_csv(csvFile, index=False)
    #            printDebug(f"Response data: {response_data}")
    #        else:
    #            print(f"Team already exists with ID: {row['teamId']}")

    #Check the API type we're requesting, extract csv data, build payload, call Gremlin API
    if apiType == "service":    
        for index, row in df.iterrows():
            printDebug(f"Processing row {index + 1}")
        
            gremlinName = row['serviceName']
            teamId = row['teamId']
            owningTeamId = teamId
            k8sName = row['k8sName']
            namespace = row['namespace']
            kind = row['kind']
            clusterId = row['clusterId']
            serviceIdCpu = row['serviceIdCpu']
            serviceIdLatency = row['serviceIdLatency']
            serviceIdNetwork = row['serviceIdNetwork']

            printDebug(f"Values - {gremlinName}, {teamId}, {owningTeamId}, {k8sName}, {namespace}, {kind}, {clusterId}")
            #Check if the service is already created and skip, or script was run and failed leaving "None"
            if not row['serviceId'] or row['serviceId'] == "None":
                jsonPayload = build_service_payload(teamId, gremlinName, owningTeamId, k8sName, namespace, kind, clusterId, serviceIdCpu, serviceIdLatency, serviceIdNetwork)
                response_data = create_service(teamId, authToken, jsonPayload)
                #Grab the response data which is the service ID and write that to the CSV
                df.at[index, 'serviceId'] = str(response_data)
                df.to_csv(csvFile, index=False)
                printDebug(f"Response data: {response_data}")
            else:
                print(f"Service already exists with ID: {row['serviceId']}")
            

    if apiType == "auth":
        for index, row in df.iterrows():
            printDebug(f"Processing row {index + 1}")

            teamId = row['teamId']
            authUrl = row['authUrl']
            authName = row['authName']
                                
            printDebug(f"Values - {authUrl}, {authName}")
            #For auth creation we just overwrite / update
            jsonPayload = build_auth_payload(authUrl, authName)
            response_data = create_authentication(teamId, authToken, jsonPayload)
            printDebug(f"Response data: {response_data}")

    if apiType == "health":    
        for index, row in df.iterrows():
            printDebug(f"Processing row {index} + 1")
        
            teamId = row['teamId']
            ##Used to create a camal case name based on the service name
            #alertNameBuilder = row['serviceName'].split('-')
            #alertName = ''.join(name.capitalize() for name in alertNameBuilder)

            healthcheckBaseURL = 'http://1.1.1.1:8481/select/1234/prometheus/api/v1/query'
            healthcheckMaxLatency = 3500
            healthCheckPrivate = True
            healthcheckAuth = row['authName']

            #Create Health Checks if the serviceId has not already been set.  This loop is checking if we already wrote
            # a serviceID to the CSV and skip that entry.
            ## WIP: combine this into a single loop passthru convert to API check instead of the CSV serviceID
            if not row['serviceIdCpu']:
                healthcheckName = row['healthNameCpu']
                query_params = {
                    "query": f'ALERTS{{alertname="{healthcheckName}"}}'
                }
                encoded_query = urllib.parse.urlencode(query_params)
                healthcheckURL = f"{healthcheckBaseURL}?{encoded_query}"
                printDebug(f"Encoded URL IS NOW {healthcheckURL}")
                healthcheckDescription = f"CPU Health Check for {row['serviceName']}"
                jsonPayload = build_healthcheck_payload(healthcheckURL, healthcheckName, healthcheckDescription, healthcheckMaxLatency, healthCheckPrivate, healthcheckAuth)
                response_data = create_healthcheck(teamId, authToken, jsonPayload)
                #Grab the response data which is the service ID and write that to the CSV
                df.at[index, 'serviceIdCpu'] = response_data
                df.to_csv(csvFile, index=False)
            else:
                print(f"CPU health check already exists with ID: {row['serviceIdCpu']}")

            if not row['serviceIdLatency']:
                healthcheckName = row['healthNameLatency']
                query_params = {
                    "query": f'ALERTS{{alertname="{healthcheckName}"}}'
                }
                encoded_query = urllib.parse.urlencode(query_params)
                healthcheckURL = f"{healthcheckBaseURL}?{encoded_query}"
                printDebug(f"Encoded URL IS NOW {healthcheckURL}")
                healthcheckDescription = f"Latency Health Check for {row['serviceName']}"
                jsonPayload = build_healthcheck_payload(healthcheckURL, healthcheckName, healthcheckDescription, healthcheckMaxLatency, healthCheckPrivate, healthcheckAuth)
                response_data = create_healthcheck(teamId, authToken, jsonPayload)
                #Grab the response data which is the service ID and write that to the CSV
                df.at[index, 'serviceIdLatency'] = response_data
                df.to_csv(csvFile, index=False)
            else:
                print(f"Latency health check already exists with ID: {row['serviceIdLatency']}")

            if not row['serviceIdNetwork']:
                healthcheckName = row['healthNameUp']
                query_params = {
                    "query": f'ALERTS{{alertname="{healthcheckName}"}}'
                }
                encoded_query = urllib.parse.urlencode(query_params)
                healthcheckURL = f"{healthcheckBaseURL}?{encoded_query}"
                printDebug(f"Encoded URL IS NOW {healthcheckURL}")
                healthcheckDescription = f"UpCheck Health Check for {row['serviceName']}"
                jsonPayload = build_healthcheck_payload(healthcheckURL, healthcheckName, healthcheckDescription, healthcheckMaxLatency, healthCheckPrivate, healthcheckAuth)
                response_data = create_healthcheck(teamId, authToken, jsonPayload)
                #Grab the response data which is the service ID and write that to the CSV
                df.at[index, 'serviceIdNetwork'] = response_data
                df.to_csv(csvFile, index=False)
            else:
                print(f"Network health check already exists with ID: {row['serviceIdNetwork']}")


        
###############################################################################
## Build the service payload
##  gremlinName = The convience display name in the Gremlin UI
##  k8sName = The actual deplyoment name in K8
###############################################################################
def build_service_payload(teamId, gremlinName, owningTeamId, k8sName, namespace, kind, clusterId, serviceIdCpu, serviceIdLatency, serviceIdNetwork, container_selection_type="ANY", container_names=None):

    payload = {
        "teamId": teamId,
        "targetingStrategy": {
            "type": "Kubernetes",
            "names": [
                {
                    "owningTeamId": owningTeamId,
                    "name": k8sName,
                    "namespace": namespace,
                    "kind": kind,
                    "clusterId": clusterId
                }
            ],
            "containerSelection": {
                "selectionType": container_selection_type,
                "containerNames": container_names
            },
            "allSet": False
        },
        "name": gremlinName,
        "statusCheckIds": [
            serviceIdCpu,
            serviceIdLatency,
            serviceIdNetwork
        ]
    }
    
    printDebug(f"Created JSON payload: {json.dumps(payload, indent=4)}")
    return payload


###############################################################################
## Build the authentication payload
##  url = URL to authenticate against
##  authName = The convience name in Gremlin UI health check dropdown
##  token = Not implimented yet
###############################################################################
def build_auth_payload(authUrl, authName, authToken=None):

    payload = {
        "url": authUrl,
        "headers": {},
        "name": authName,
        "privateNetwork": True,
        "lastAuthenticationStatus": "AUTHENTICATED",
        "integrationSpecificValues": {}
    }
    
    printDebug(f"Created JSON payload: {json.dumps(payload, indent=4)}")
    return payload


###############################################################################
## Build the healthcheck payload
##  url = URL to authenticate against
##  authName = The convience name in Gremlin UI health check dropdown
##  token = Not implimented yet
###############################################################################
def build_healthcheck_payload(healthcheckURL, healthcheckName, healthcheckDescription, healthcheckMaxLatency, healthCheckPrivate, healthcheckAuth):

    payload = {
        "isContinuous": True,
        "isPrivateNetwork": healthCheckPrivate,
        "name": healthcheckName,
        "description": healthcheckDescription,
        "thirdPartyPresets": "custom",
        "endpointConfiguration": {
            "url": healthcheckURL,
            "method": "GET"
        },
        "evaluationConfiguration": {
            "okLatencyMaxMs": healthcheckMaxLatency,
            "okStatusCodes": [
                "200"
            ]
        },
        "teamExternalIntegration": {
            "observabilityToolType": "CUSTOM",
            #"domain": "null",
            "name": healthcheckAuth
        }
    }

    printDebug(f"Created JSON payload: {json.dumps(payload, indent=4)}")
    return payload


###############################################################################
## Debugging printout enabled with CLI option --debug
###############################################################################
def printDebug(message):
    if DEBUG:
        print(f"DEBUG: {message}")


###############################################################################
## Main function
##   First create a team (WIP)
##   Next create the authentication for Health Checks
##   Next create the Health Checks and write the IDs to the csv
##   Finally build the service and attach health checks
###############################################################################
def main(csvFile, authToken):
    
    #fetch_services(teamId, authToken, serviceId = None)
    #printDebug("!!! Stage 1: Create Teams !!!")
    #execute_API(csvFile, authToken, "team")
    printDebug("!!! Stage 2: Setup Health Check authentication !!!")
    execute_API(csvFile, authToken, "auth")
    printDebug("!!! Stage 3: Setup Health Checks !!!")
    execute_API(csvFile, authToken, "health")
    printDebug("!!! Stage 4: Create Services !!!")
    execute_API(csvFile, authToken, "service")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read a CSV file and make API calls to api.gremlin.com.")
    parser.add_argument('--debug', action='store_true', help="Enable debugging")
    parser.add_argument('csvFile', type=str, help='Path to the CSV file')
    parser.add_argument('authType', type=str, choices=["Key","Bearer"], help='Choose the authentication type')
    parser.add_argument('authToken', type=str, help='Bearer or Key for authentication')
    args = parser.parse_args()
    DEBUG = args.debug
    AUTHTYPE = args.authType
    main(args.csvFile, args.authToken)
