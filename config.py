NETWORK = {
    "db": {
        "DB_DRIVER": "mysql+pymysql",
        "DB_HOST": "localhost",
        "DB_USER": "snet",
        "DB_PASSWORD": "Password!12345",
        "DB_NAME": "snet_converter_db",
        "DB_PORT": 3306,
        "DB_LOGGING": True,
    },
}

SLACK_HOOK = {
    "hostname": "",
    "port": 443,
    "path": "",
    "method": "POST",
    "headers": {"Content-Type": "application/json"},
}