import paramiko

class SSHConnector():
    def __init__(self, hostname, port, device_type, username, password) -> None:
        """
        Connection handler construction 

        Args:
            hostname (str): address/name of the device
            args : ['username', 
                    'password', 
                    'secret'
                    'device_type', 
                    'port']
        """

        self.hostname = hostname
        self.port = port
        self.device_type = device_type
        self.username = username
        self.password = password
        self.ssh = None
    
    def connect_to_router(self):
        # Create an SSH client
        self.ssh = paramiko.SSHClient()

        # Automatically add the server's host key 
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the router
        self.ssh.connect(self.hostname, username=self.username, password=self.password)

        return self.ssh

    def execute_command(self, command):
        
        # Execute a command on the router
        output = self.ssh.exec_command(command)
        
        if isinstance(output, tuple):
            output = output[1].read().decode('utf-8')  

        # Parse interface information
        interface_lines = [line.strip() for line in output.split('\n')]
        
        interfaces = []
        for line in interface_lines[1:]: 
            columns = line.split()
            if len(columns) >= 5:
                interface = columns[0]
                ip_address = columns[1]
                status = columns[4]
                interfaces.append({"interface": interface, "ip_address": ip_address, "status": status})
                
        
        return interfaces[3:]
    
    def disconnect(self):
        if self.ssh:
            self.ssh.close()
            