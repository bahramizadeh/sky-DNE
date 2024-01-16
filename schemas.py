"""
    Using Marshmallow library to serialize and deserialize data  
    """
from marshmallow import Schema, fields

class UserSchema(Schema):
    """
    this is a schema for serializing and deserializing the payload of User requests
    arguments: username and password
    """
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    
    