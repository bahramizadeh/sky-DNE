# General libraries
import os
import sys
import xmltodict

from loguru import logger

from jinja2 import Environment, FileSystemLoader
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint
from flask.views import MethodView

# Internal modules
from connectors.netconf import NetconfHandler
from connectors.cliconf import SSHConnector
from schemas import ConfigDataSchema




###########
# Logging #
###########
log_level = os.environ.get("log_level","INFO")
logger.add(sys.stderr, format="{time} {level} {message}", level=log_level)


blp = Blueprint("LoopBacks","LoopBacks",description="Operations on LoopBacks")



@blp.route("/interfaces/loopback/<int:loopback_num>")
class LoopbackConfing(MethodView):
    
    
    # Config router
    @jwt_required(fresh=True)
    @blp.arguments(ConfigDataSchema)
    def post(self, config_data, loopback_num):
        
        connection_data = config_data.get('connection_data')
        loopback_data = config_data.get("loopback_data")
        loopback_data['loopback_number'] = loopback_num
        
        # Copy loopback_data in new dictionaries to provide suitable dictionary for jinja2 template
        loopback_edit_data = loopback_data.copy()
        loopback_edit_data['operation'] = 'config'
        
        
        loopback_filter_data = loopback_data.copy()
        loopback_filter_data['operation'] = 'filter'
        
        template = "loopback.xml"
        template_path = "templates/"

        file_loader = FileSystemLoader(template_path)
        env = Environment(loader=file_loader)
        template = env.get_template(template)
        
        loopback_edit_payload = template.render(data=loopback_edit_data)
        loopback_filter_payload = template.render(data=loopback_filter_data)
        
        # Router pre-check to make sure loopback does not exists
        pre_check_result = self.check_config(connection_data, loopback_filter_payload)

        # Config router if loopback does not exists
        if not pre_check_result['data']:
            response = self.edit_configuration(connection_data, loopback_edit_payload)
            
            # Router post-check to make sure the config is done
            post_check_result = self.check_config(connection_data, loopback_filter_payload)
            if post_check_result['data']:
                response['data'] = post_check_result['data']
                
            
            return response
        
        return {
                "status": "failure",
                "message": f"The operation failed, loopback {loopback_num} already exists",
                "data": pre_check_result['data']
            }

    
    # Delete the router configuration
    @jwt_required(fresh=True)
    @blp.arguments(ConfigDataSchema)
    def delete(self, config_data, loopback_num):

        connection_data = config_data.get('connection_data')
        # Copy config_data in new dictionary loopback_data and add the below keys and values into the new dictionary
        loopback_data = config_data.copy()
        loopback_data['loopback_number'] = loopback_num
        loopback_data['delete'] = True
        loopback_data['operation'] = 'config'
        
        
        template = "loopback.xml"
        template_path = "templates/"

        file_loader = FileSystemLoader(template_path)
        env = Environment(loader=file_loader)
        template = env.get_template(template)
        loopback_payload = template.render(data=loopback_data)

        response = self.edit_configuration(connection_data, loopback_payload)
        if response['status'] == "success":
            response['message'] = f"Loopback {loopback_num} was successfully removed"
        if response['status'] == "failure":
            response['message'] = f"Loopback {loopback_num} does not exist, check the current configuration"
        return response


    def edit_configuration(self, connection_data, loopback_payload):
        try:
            ncc = NetconfHandler(**connection_data)
            ncc_connection = ncc.connection()
            logger.info("\n [+] Netconf Connection successfully established")    
        except Exception as e:
            logger.warning(f"\n [+] Connection Failure: \n {e}")
           
            return {
                "status": "failure",
                "message":"The operation failed",
                "data": f"\n [+] Connection Failure: \n {e}"
            }, 400
        # Send NETCONF <edit-config>
        try:
            with ncc_connection.locked(target="candidate"):
                ncc_connection.edit_config(loopback_payload, target="candidate")
                ncc_connection.commit()
                ncc.save_config(ncc_connection)
            
        except Exception as e:
            return {
                "status": "failure",
                "message":"The operation failed",
                "data": f"Check the current configuration or IP address and mask \n {e}"
            }
          
        return {
            "status": "success",
            "message": "operation is successfully done",
            "data": None
        }
    
    def check_config(self, connection_data, loopback_payload):
        try:
            ncc = NetconfHandler(**connection_data)
            ncc_connection = ncc.connection()
            logger.info("\n [+] Netconf Connection successfully established")    
        except Exception as e:
            logger.warning(f"\n [+] Connection Failure: \n {e}")
            return {
                "status": "failure",
                "message": "operaion failed",
                "data": f"\n [+] Connection Failure: \n {e}"
            }

        # Send NETCONF <get-config>
        try:
            with ncc_connection:
                response_xml = ncc_connection.get_config(filter=loopback_payload, source="running")
                response_xml = str(response_xml)
                response_data = xmltodict.parse(response_xml)
                loopback_cfg = response_data.get('rpc-reply', {}).get('data')
            
        except Exception as e:
            return {
                "status": "failure",
                "message": "The operation failed",
                "data": f"Check Netconf Connection \ {e}"
            }
        return {
                "status": "success",
                "message": "operation is successfully done",
                "data": loopback_cfg
            }


@blp.route("/interfaces/status")
class InterfacesStatusResource(MethodView):
    
    @blp.arguments(ConfigDataSchema)
    def post(self, config_data):
        
        connection_data = config_data.get('connection_data')

        try:
            connector = SSHConnector(**connection_data)
            # Connect to the router
            ssh = connector.connect_to_router()
            logger.info("\n [+] Paramiko Connection successfully established")    
        except Exception as e:
            logger.warning(f"\n [+] Connection Failure: \n {e}")
            return {
                "status": "failure",
                "message": "operaion failed",
                "data": f"\n [+] Connection Failure: \n {e}"
            }
        
        try:
            # Example: Execute a command on the router
            command_to_execute = 'show ip interface brief' 
            response = connector.execute_command(command_to_execute)
        
            # Close the SSH connection when done
            connector.disconnect()
        
        except Exception as e:
            return {
                "status": "failure",
                "message": "The operation failed",
                "data": f"Check Netconf Connection \ {e}"
            }
            
            
        return response
    