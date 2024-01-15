import json

def lambda_handler(event, context):
    x = event['X']
    y = event['Y']
    z = event['Z']
    
    if x == 0 or y == 0 or z == 0:
        return {
            'statusCode': 200,
            'body': json.dumps('One of the variables is zero')
        }
    else:
        result = x * y * z
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
