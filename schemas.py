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
    
    
class ConnectionSchema(Schema):
    hostname = fields.Str(required=True)
    port = fields.Int(required=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    device_type = fields.Str(required=True)
    
        
class LoopBackDataSchema(Schema):
    ipv4 = fields.IPv4(required=False)
    ipv4_mask = fields.IPv4(required=False)
    
class ConfigDataSchema(Schema):
    connection_data = fields.Nested(ConnectionSchema)
    loopback_data = fields.Nested(LoopBackDataSchema)