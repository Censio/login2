import json
import boto3
import uuid
from datetime import datetime

def lambda_handler(event, context):
    HTTP_METHODE = event["requestContext"]["http"]["method"]
    HTTP_PATH = event["requestContext"]["http"]["path"]

    if HTTP_METHODE == "GET" and HTTP_PATH == "/":
        STATUS_CODE, HEADERS, BODY = getMainPage(event)
    elif HTTP_METHODE == "GET" and HTTP_PATH == "/sessionid":
        STATUS_CODE, HEADERS, BODY = getSessionID(event)
    elif HTTP_METHODE == "GET" and HTTP_PATH == "/load":
        STATUS_CODE, HEADERS, BODY = getRansomePage(event)
    elif HTTP_METHODE == "POST" and HTTP_PATH == "/addevent":
        STATUS_CODE, HEADERS, BODY = postSendEvent(event)
    else:
        STATUS_CODE, HEADERS, BODY = getMainPage(event)

    return {
        "statusCode": STATUS_CODE,
        "headers": HEADERS,
        "body": BODY,
        "cookies": [],
        "isBase64Encoded": False
    }

def getMainPage(event):
    with open('files/index.html', 'r') as file:
        BODY = file.read()

    STATUS_CODE = 200
    HEADERS = {
        "Content-Type": "text/html",
        "Access-Control-Allow-Origin": "https://nx7vlzavtmlon7odbcyr6frgo40fwehp.lambda-url.us-east-1.on.aws",
        "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"

    }
    return STATUS_CODE, HEADERS, BODY

def getSessionID(event):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('cmt-nemesztkerested-test')

    # new session id
    sessionId = str(uuid.uuid4())
    table.put_item(Item={'pk':sessionId, 'actions':[]})

    # store sessionid created event
    response = table.get_item(Key={'pk': sessionId})
    item = response['Item']
    item['actions'].append({
        "action_name": "Session ID was created",
        "time": datetime.now().strftime("%m/%d/%Y, %H:%M:%S %Z")
    })
    table.put_item(Item=item)

    STATUS_CODE = 200
    HEADERS = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "https://nx7vlzavtmlon7odbcyr6frgo40fwehp.lambda-url.us-east-1.on.aws",
        "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"
    }
    BODY = json.dumps({'sessionid': sessionId})
    return STATUS_CODE, HEADERS, BODY


def postSendEvent(event):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('cmt-nemesztkerested-test')

    try:
        requestJSON = json.loads(event["body"])
        response = table.get_item(Key={'pk': requestJSON['sessionid']})
        item = response['Item']
        item['actions'].append({
            "action_name": requestJSON['action_name'],
            "action_details": requestJSON['action_details'],
            "time": datetime.now().strftime("%m/%d/%Y, %H:%M:%S %Z")
        })
        table.put_item(Item=item)
        STATUS_CODE = 200
        HEADERS = {}
        BODY = json.dumps({'ok': "200"})
        return STATUS_CODE, HEADERS, BODY
    except Exception as e:
        table.put_item(Item=item)
        STATUS_CODE = 200
        HEADERS = {}
        BODY = json.dumps({'error': str(e)})
        return STATUS_CODE, HEADERS, BODY

def getRansomePage(event):
    with open('files/ransom_message1.html', 'r') as file:
        BODY = file.read()

    STATUS_CODE = 200
    HEADERS = {
        "Content-Type": "text/html",
        "Access-Control-Allow-Origin": "https://nx7vlzavtmlon7odbcyr6frgo40fwehp.lambda-url.us-east-1.on.aws",
        "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"

    }
    return STATUS_CODE, HEADERS, BODY