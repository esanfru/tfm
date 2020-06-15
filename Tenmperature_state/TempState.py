import logging
from datetime import datetime
from random import randint

import boto3
from botocore.exceptions import ClientError

# Initialized DynamoDB client
# Note this creates a dynamodb table in region us-east-1 (N. Virginia)
# Change the region name to something different if you like
# Note endpoint and aws credentials are not specified. By default this
# uses the credentials configured for the session. See Boto 3 docs
# for more details.

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
tableName = "TempStats"

# Create the dynamo db table if needed
try:
    table = dynamodb.create_table(
        TableName=tableName,
        KeySchema=[{"AttributeName": "Time", "KeyType": "HASH"}],  # Partition key
        AttributeDefinitions=[{"AttributeName": "Time", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    # Wait until the table exists.
    table.meta.client.get_waiter("table_exists").wait(TableName=tableName)
except ClientError as e:
    if e.response["Error"]["Code"] == "ResourceInUseException":
        print("Table already created")
    else:
        raise e

# initialize the logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# This handler is called when an event is sent via MQTT
# Event targets are set in subscriptions settings
# This should be set up to listen to shadow document update


def function_handler(event, context):

    logger.info(event)
    data = event["current"]["state"]["reported"]
    if data:
        global tableName
        logger.info(f'Cars passed during green light: {json.dumps(event["current"]["state"]["reported"])}' )
        table = dynamodb.Table(tableName)
        data_prot = {
                "Time": str(datetime.utcnow())
                }
        data_prot.update(data)
        table.put_item(
            Item=data_prot
        )
    return
