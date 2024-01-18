# Sky DNE 
## Overview

This repository contains the python codes for configuration loopback for a router Iosxe via netconf and paramiko.
FastAPI is the web framework is used to handle all APIs.

```
1- Some parts of APIs are implemented to work with Netconf/YANG to configure a loopback interface and delete it.
2- Some parts of APIS are implemented to deal wit CLI and paramiko to return all interfaces include loopback interfaces with their status and IP adresses
3- Requred postman collections to work with API
```

### Prerequirements
```
1- Python3.10
2- Docker and docker-compose
3- Install all required dependencies inside the requirements.txt
```

### How to setup the project

docker-compose setup:

```
1- IOSXE17.9.2 or higher version
2- docker-compose build
3- docker-compose up 
4- Import postman collection from "SkyDNE_Postman_collection" directory
5- Turn on the router and setup ip, username, ssh, netconf, yang
6- Use correct ip, username, password and device_type in order to connect the router
7- test APIs using postman collections and see the results
```

local setup:

```
1- Create python virtual environment
2- Install all packages in requirements.txt
3- activate virtual environment usering this command: source virtual_env_name/bin/activate
4- pip install -r requirements.txt
5- run this command: flask run -p 5050 --host 0.0.0.0
6- IOSXE17.9.2 or higher version
7- Import postman collection from "SkyDNE_Postman_collection" directory
8- Turn on the router and setup ip, username, ssh, netconf, yang
9- Use correct ip, username, password and device_type in order to connect the router
10- test APIs using postman collections and see the results
```


### API Explanations
 
**"Post --> /interfaces/loopback/<int:loopback_num>":**
> This API is used to configure a loopback interface of the router via netconf connection

**"Delete --> /interfaces/loopback/<int:loopback_num>":**
> This API is used to delete the configuration of the loopback interface from the router via netconf connection

**"Post --> /interfaces/status":**
> This API is used to post connection data to connect to the router and return all interfaces including interface, status and Ip address from the router via cli and paramiko