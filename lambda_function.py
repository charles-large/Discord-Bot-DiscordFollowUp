import json
import urllib3
import time
import boto3

def lambda_handler(event, context):
    # print(event)
    token = event['token']
    app_id = event['application_id']
    url = f"https://discord.com/api/webhooks/{app_id}/{token}"
    
    
    client = boto3.client('cloudformation')
    
    while True:
        try:
            #Gets the Stack Status if the stack exists#
            response = client.describe_stacks(StackName = event['StackName'])
            StackStatus = response['Stacks'][0]['StackStatus']
        
            if StackStatus == "CREATE_IN_PROGRESS":
                time.sleep(15)
                continue
            
            elif StackStatus == "DELETE_IN_PROGRESS":
                time.sleep(15)
                continue
                
            elif StackStatus == "CREATE_COMPLETE":
                try:
                    #Returns IP address of the instance deployed#
                    ip = response['Stacks'][0]['Outputs'][0]['OutputValue']
                    http = urllib3.PoolManager()
                    data = {"content": f'Server IP: {ip}'}
                    x = http.request('POST', url=url, body=json.dumps(data), headers={'Content-Type': 'application/json'}, retries=True)
                    break
                except Exception as e:
                    #If this fails, the outputs of the CF template may need more time to propogate. It will continue to retry#
                    time.sleep(15)
                    continue
            
            elif StackStatus == "ROLLBACK_IN_PROGRESS":
                #This occurs in the case of error in stack deployment#
                http = urllib3.PoolManager()
                data = {"content": f'Stack Failed. Rolling Back Stack.'}
                x = http.request('POST', url=url, body=json.dumps(data), headers={'Content-Type': 'application/json'}, retries=True)
                time.sleep(25)
                continue
                
            elif StackStatus == "ROLLBACK_COMPLETE":
                try:
                    #Will delete the stack onces rollback completes#
                    response = client.delete_stack(StackName = event['StackName'])
                    continue
                except Exception as e:
                    print(e)
                    break
        except:
            try:
                #If when describing the stack it does not exist, the program assumes successfull deletion#
                http = urllib3.PoolManager()
                data = {"content": f'Delete Completed Successfully'}
                x = http.request('POST', url=url, body=json.dumps(data), headers={'Content-Type': 'application/json'}, retries=True)
                break
            except Exception as e:
                time.sleep(15)
                break