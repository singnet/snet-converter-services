def get_blockchain(event, context):
    print("Welcome")
    return {
        "statusCode": 200,
        "body": "Welcome test",
        "headers": {"Content-Type": "application/json"},
    }