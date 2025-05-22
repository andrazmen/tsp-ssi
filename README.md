## Introduction
Clone repository:

```bash
git clone https://git.e5.ijs.si/andrazm/tsp-ssi.git
```

## A Cloud Agent Python
Using pip package.

Create virutal environment:
```bash
python3 -m venv .venv_aca-py
source .venv_aca-py/bin/activate
```

Install package:
```bash
pip install acapy-agent==1.1.1
```

## Aries CloudController
Clone repository:
```bash
git clone https://github.com/didx-xyz/aries-cloudcontroller-python.git
```

Create virtual environment:
```bash
python3 -m venv .venv_cloudcontroller
source .venv_cloudcontroller/bin/activate
```

Change directory:
```bash
cd aries-cloudcontroller-python/
```

Install requirements and package in editable mode (For now, in future it will probably be installed directly, not in editable mode):
```bash
pip install -r requirements.txt 
pip install --no-cache-dir -e .
```

Downgrade aiohttp, because of event_loop errors:
```bash
pip uninstall aiohttp

pip install aiohttp==3.9.4
```

Install Quart for webhook server:
```bash
pip instal Quart==0.20.0
```

## VON Network
Using docker.

Clone repository:
```bash
git clone https://github.com/bcgov/von-network.git
```

Change directory:
```bash
cd von-network
```

Build and start docker image:
```bash
./manage build

./manage start
./manage logs
```

## Indy Tails Server
Using docker.

Clone repository:
```bash
git clone https://github.com/bcgov/indy-tails-server.git
```

Change directory:
```bash
cd indy-tails-server/docker
```

Build docker image:
```bash
./manage build
```

Set *NGROK_AUTHTOKEN*:
```bash
docker-compose.yml
NGROK_AUTHTOKEN=<your token here>
```

Start docker container:
```bash
./manage start
./manage logs
```

## Running a code
## Starting von-network and indy tails server
VON-network is a development and test Hyperledger Indy Node network. Indy Tails Server is file server that is designed to receive, store and serve Hyperledger Indy Tails files, essential for credential revocation.

```bash
cd von-network

./manage start 193.138.1.21 WEB_SERVER_HOST_PORT=80 "LEDGER_INSTANCE_NAME=My Ledger" --logs
```

```bash
cd indy-tails-server/docker

./manage start 193.138.1.21 --logs
```

## Starting aca-py agents
Directory ```args``` contains ```.yaml``` files with start up parameters for ACA-Py agents. To start ```user``` digital agent ```--arg-file``` argument is needed to specify the path to a ACA-Py arguments file. To run ACA-py agent that connects to previously started von-network, the DID needs to be published. The easiest way to do this is to use von-network web server running on ```http://193.138.1.21```, where DID is registered from the seed defined in argument file under parameter ```seed```.

```bash
source .venv_aca-py/bin/activate

aca-py start --arg-file args/user.yaml
```

## Starting controller
Controller is business logic that controls ACA-py instance through HTTP requests and webhook notifications. In order to run controller logic, ACA-py agent need to run! 

Directory ```controllers``` contains controller logic. File ```controller.py``` implements universal controller used for User, Aggregator, EDO and Technical Aggregator instances. VCS has its own controller logic wrapped in ```vcs.py``` file. Directory ```config``` contains configuration files for controllers. Accordingly, ```--config``` argument is required to specify the path to a specific configuration file.

```bash
source .venv_cloudcontroller/bin/activate

cd controllers

python3 controller.py --config config/user_config.py 
```

### Universal controller
Universal controller provides following CLI commands:

```
- dids                      lists all DID identifiers saved in digital wallet
- create did                create new DID identifier with sov method
- public did                returns current public DID identifier
- assign did                assigns DID identifier for the new public DID identifier
- url                       returns the URL of last created invitation
- create inv                creates new connection invitation and displays invitation URL
- receive inv               takes invitation URL and extracts connection invitation
- accept inv                agrees on received connection invitation and send DID Exchange request
- delete inv                deletes connections created with specific invitation
- accept didx req           accepts DID Exchange request and answers back with DID Exchange response
- reject didx               rejects DID Exchange request or response and cancels establishing connection process
- conns                     lists all connections (active and inactive)
- conn                      returns specific connection and its data
- delete conn               removes connection so its no longer usable (can't send or receive any messages or requests)
- ping                      sends trust ping over selected connection
- message                   sends message over connection using Basic Message protocol
- schemas                   lists all published schemas IDs
- schema                    returns selected pubished schema ID and its information
- publish schema            publishes schema with defined name, version and attributes
- cred defs                 lists all created credential definitions IDs
- cred def                  returns selected credential definition ID and its information
- create cred def           creates new credential definition based on selected published schema
- rev regs                  lists all revocation registries IDs created when credential definition was created
- rev reg                   returns selected revocation registry ID and its information
- active rev reg            lists current active revocation registry (two are created, when first is full second is used)
- rev reg issued            returns number of issued credentials under selected revocation registry
- rev reg issued details    returns details of issued credentials under selected revocation registry
- revoke                    revokes selected credential
- rev status                returns credential's revocation status (either stored (holder) or issued (issuer))
- vc records                lists all credential exchange records
- vc record                 returns selected credential exchange record
- delete vc record          removes selected credential exchange record
- vc problem                sends credential exchange problem report and abandons the exchange
- vc offer                  sends credential offer
- vc request                send credential request
- issue vc                  issues credential
- store vc                  stores received credential in digital wallet
- vcs                       lists all stored credentials
- vc                        returns selected credential and its information
- delete vc                 removes stored credential from digital wallet
- vp records                lists all presentation exchange records
- vp record                 returns selected presentation exchange record
- delete vp record          removes selected presentation exchange record
- vp problem                sends presentation exchange problem report and abandons the exchange
- vp proposal               sends presentation proposal
- vp request                sends presentation request
- matching vc               lists stored credentials that match received presentation request
- send vp                   sends presentation
- verify                    verifies received presentation
```

### VCS controller
VCS controller provides following CLI commands:

```
- dids                      lists all DID identifiers saved in digital wallet
- create did                create new DID identifier with sov method
- public did                returns current public DID identifier
- assign did                assigns DID identifier for the new public DID identifier
- url                       returns the URL of last created invitation
- create inv                creates new connection invitation and displays invitation URL
- receive inv               takes invitation URL and extracts connection invitation
- accept inv                agrees on received connection invitation and send DID Exchange request
- delete inv                deletes connections created with specific invitation
- accept didx req           accepts DID Exchange request and answers back with DID Exchange response
- reject didx               rejects DID Exchange request or response and cancels establishing connection process
- conns                     lists all connections (active and inactive)
- conn                      returns specific connection and its data
- delete conn               removes connection so its no longer usable (can't send or receive any messages or requests)
- ping                      sends trust ping over selected connection
- message                   sends message over connection using Basic Message protocol
- vp records                lists all presentation exchange records
- vp record                 returns selected presentation exchange record
- delete vp record          removes selected presentation exchange record
- vp problem                sends presentation exchange problem report and abandons the exchange
- vp request                sends presentation request
- verify                    verifies received presentation
- proofs                    lists all stored verified and valid presentations
```

## ACS and MQTT access control
Access control service (ACS) deployment is accessible at the following location: https://git.e5.ijs.si/dusan/tsp.git. Repository includes instructions to generate and deploy Certificate Authority and to make server certificate for the ACS server and user certificate for clients.

In ACS code, authorization engine for MQTT protocol is added, supporting SSI credentials. Based on SSI credential support, 2 access policies are defined.

Repository includes instructions for installing, patching, configuring and running Mosquitto MQTT broker.

### Starting ACS
```bash
source .venv_tsp/bin/activate
cd tsp
export PYTHONPATH=$(pwd)

python acs/acs.py --keystore=CA-si/server-certificates/andraz.e5.ijs.si.p12 --ssl
```

### Starting MQTT broker
sudo systemctl start mosquitto

#logs
sudo journalctl -u mosquitto.service -n 15
sudo tail -f /var/log/mosquitto/mosquitto.log

#### Testing MQTT
```
LISTENER:
(.venv_tsp) andraz@andraz:~/tsp$ python bin/secure_mqtt_listener.py -s andraz.e5.ijs.si -p 8883 -k /home/andraz/tsp/CA-si/user-certificates/test_listener.p12 -t /cem/test -d -r

(.venv_tsp) andraz@andraz:~/tsp$ python bin/secure_mqtt_listener.py -s andraz.e5.ijs.si -p 8883 -k /home/andraz/tsp/CA-si/user-certificates/si.manager@resonance.si.p12 -t /cem/si.manager@resonance.si.p12 -d -r

python bin/secure_mqtt_listener.py -s andraz.e5.ijs.si -p 8883 -k /home/andraz/tsp/CA-si/user-certificates/cf0a72fb-2661-4ec2-99f7-95fa3b0b1229.p12 -t /cem/cem1 -d -r

python bin/secure_mqtt_listener.py -s andraz.e5.ijs.si -p 8883 -k /home/andraz/tsp/CA-si/user-certificates/fcc931cf-8ed2-4a18-95b6-daca83a31894.p12 -t /cem/cem1/devices -d -r

PUBLISHER:
(.venv_tsp) andraz@andraz:~/tsp$ python bin/secure_mqtt_publisher.py -s andraz.e5.ijs.si -p 8883 -k /home/andraz/tsp/CA-si/user-certificates/test_publisher.p12 -t /cem/test -m '{"key": "value"}'

(.venv_tsp) andraz@andraz:~/tsp$ python bin/secure_mqtt_publisher.py -s andraz.e5.ijs.si -p 8883 -k /home/andraz/tsp/CA-si/user-certificates/si.manager@resonance.si.p12 -t /cem/si.manager@resonance.si -m '{"key": "value"}'

python bin/secure_mqtt_publisher.py -s andraz.e5.ijs.si -p 8883 -k /home/andraz/tsp/CA-si/user-certificates/cf0a72fb-2661-4ec2-99f7-95fa3b0b1229.p12 -t /cem/cem1 -m '{"key": "value"}'

python bin/secure_mqtt_publisher.py -s andraz.e5.ijs.si -p 8883 -k /home/andraz/tsp/CA-si/user-certificates/fcc931cf-8ed2-4a18-95b6-daca83a31894.p12 -t /cem/cem1/control -m '{"key": "value"}'
```