from os import getenv
from pathlib import Path

def get_connection_parameters():
    """ Get connection parameters for Snowflake connection """
    connection_parameters = {
        "account": "myaccount",
        "user": "me",
        "private_key_file": "myprivkey",
        "private_key_file_pwd" : "myprivkeypwd".encode("UTF-8"),
        "role": "myrole",
        "warehouse": "mywarehouse",
        "database": "mydatabase",
        "schema": "myschema"
    }
    return connection_parameters
