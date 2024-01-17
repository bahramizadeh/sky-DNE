from ncclient import manager, xml_


class NetconfHandler():
    def __init__(self, hostname, port, device_type, username, password) -> None:
        
        """
        Connection handler construction 

        Args:
            hostname (str): address/name of the device
            args : ['username', 
                    'password', 
                    'device_type', 
                    'port']
        """

        self.hostname = hostname
        self.port = port
        self.device_type = device_type
        self.username = username
        self.password = password
        
        
    def connection(self):
        
        """
        Establishes netconf connection to the target device
        """
        
        connection_data = {
            "host" : self.hostname,
            "port":self.port,
            "username":self.username,
            "password":self.password,
            "hostkey_verify":False,
            "device_params" : {"name": self.device_type},
            "timeout" : 10,
        }

        NCConnection = manager.connect(**connection_data)
        return NCConnection


    def save_config(self, nc_manager):
        
        # Build "save" XML Payload for the RPC
        save_body = ("<cisco-ia:save-config xmlns:cisco-ia='http://cisco.com/yang/cisco-ia'/>")
        
        # Send the RPC to the Device
        nc_manager.dispatch(xml_.to_ele(save_body))