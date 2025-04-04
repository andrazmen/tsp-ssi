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

- `dids`  
  Lists all DID identifiers saved in digital wallet.

- `create did`  
  Create new DID identifier with sov method.

- `public did`  
  Lists current public DID identifier.

- `assign did`  
  Assigns DID identifier for the new public DID identifier.

- `url`  
  Returns the URL of last created invitation.

- `create inv`  
  Creates new connection invitation and displays invitation URL.

- `receive inv`  
  Takes invitation URL and extracts connection invitation.

- `accept inv`  
  Agrees on received connection invitation and send DID Exchange request.

- `delete inv`  
  Deletes connections created with specific invitation.

- `accept didx req`  
  Accepts DID Exchange request and answers back with DID Exchange response.

- `reject didx`  
  Rejects DID Exchange request or response and cancels establishing connection process.

- `conns`  
  Lists all connections (all possible states).

- `conn`  
  Lists specific connection and its data.

- `delete conn`  
  Removes connection so its no longer usable (can't send or receive any messages or requests).

- `ping`  
  Sends trust ping over selected connection.

- `message`  
  Sends message over connection using Basic Message protocol.

- `schemas`  
  Returns all published schemas.

- `schema`  
  Lists selected pubished schema and its information.

- `publish schema`  
  Publishes schema with defined name, version and attributes.

- `cred defs`  
  Lists all created credential definitions IDs.

- `cred def`  
  Returns selected credential definition ID and its information.

- `create cred def`  
  Creates new credential definition based on selected published schema.

- `rev regs`  
  Lists all revocation registries IDs created when credential definition was created.

- `rev reg`  
  Returns selected revocation registry ID and its information.

- `active rev reg`  
  Lists current active revocation registry (two are created, when first is full second is used).

- `rev reg issued`  
  Returns number of issued credentials under selected revocation registry.

- `rev reg issued details`  
  Returns details of issued credentials under selected revocation registry.

- `revoke`  
  Revokes selected credential.

- `rev status`  
  Returns credential's revocation status (either stored (holder) or issued (issuer)).

- `vc records`  
  Lists all credential exchange records.

- `vc record`  
  Returns selected credential exchange record.

- `delete vc record`  
  Removes selected credential exchange record.

- `vc problem`  
  Sends credential exchange problem report and abandons the exchange.

- `vc offer`  
  Sends credential offer.

- `vc request`  
  Send credential request.

- `issue vc`  
  Issues credential.

- `store vc`  
  Stores received credential in digital wallet.

- `vcs`  
  Lists all stored credentials.

- `vc`  
  Returns selected credential and its information.

- `delete vc`  
  Removes stored credential from digital wallet.

- `vp records`  
  Lists all presentation exchange records.

- `vp record`  
  List selected presentation exchange record.

- `delete vp record`  
  Removes selected presentation exchange record.

- `vp problem`  
  Sends presentation exchange problem report and abandons the exchange.

- `vp proposal`  
  Sends presentation proposal.

- `vp request`  
  Sends presentation request.

- `matching vc`  
  Lists credentials that match received presentation request.

- `send vp`  
  Sends presentation.

- `verify`  
  Verifies received presentation.


### VCS controller
VCS controller provides following CLI commands:

- `dids`  
  Lists all DID identifiers saved in digital wallet.

- `create did`  
  Create new DID identifier with sov method.

- `public did`  
  Lists current public DID identifier.

- `assign did`  
  Assigns DID identifier for the new public DID identifier.

- `url`  
  Returns the URL of last created invitation.

- `create inv`  
  Creates new connection invitation and displays invitation URL.

- `receive inv`  
  Takes invitation URL and extracts connection invitation.

- `accept inv`  
  Agrees on received connection invitation and send DID Exchange request.

- `delete inv`  
  Deletes connections created with specific invitation.

- `accept didx req`  
  Accepts DID Exchange request and answers back with DID Exchange response.

- `reject didx`  
  Rejects DID Exchange request or response and cancels establishing connection process.

- `conns`  
  Lists all connections (all possible states).

- `conn`  
  Lists specific connection and its data.

- `delete conn`  
  Removes connection so its no longer usable (can't send or receive any messages or requests).

- `ping`  
  Sends trust ping over selected connection.

- `message`  
  Sends message over connection using Basic Message protocol.

- `vp records`  
  Lists all presentation exchange records.

- `vp record`  
  List selected presentation exchange record.

- `vp problem`  
  Sends presentation exchange problem report and abandons the exchange.

- `vp request`  
  Sends presentation request.

- `verify`  
  Verifies received presentation.

- `proofs`  
  Lists all verified and valid presentations. 


## TODO
- (lokalno) briši env za von-network in tails-server, ker se jih zaganja v dockerju
- razmisli, če bi se cloudcontroller tudi instaliralo kar iz pip package-a (so potrebne modifikacije kode?)
- controller ne more hkrati zaganjati aca-py in cloudcontrollerja, če sta v različnih .venv (<s>se jih da v isti env?</s> Problem ker je treba downgradad aiohttp na 3.9.4 ker errorji..)
- aca-py je trenutno verzije 1.1.1, potrebno nadgradit

- <s>DIDEx trenutno narejen avtomatsko - ko nekdo sprejme naš javni invitation, se izvede DID exchange in vzpotavi povezava: treba narest ročni DID exchange</s> Oboje je možno
- preveri kateri parametri pri cred def in rev bi bili avtomatizirani
- <s>stestiraj vse revocation funkcije</s>
- <s>stestiraj /revoke (kaj potrebuješ za revoke - cred_ex_id, ali cred-rev_id in rev_reg_id)</s>
- preveri, če je potreben v praksi še kakšen endpoint iz revocation APIjev

- issue VC: preveri parametre sporočil offer, request, proposal... predvsem attributes in replacement_id (v smislu, da nov VC zamenja starega). Nastavljeno, da je flow automatic, če issuer začne z offer in ga holder sprejme.. v primeru, da se začne s proposal iz holderjeve strani, potem moramo ročno? (issue_atomated avtomatizira celoten flow, uporabno?)

- <s>get records, connections... omogoča filtriranje, zaenkrat requestas vse</s>

- revocation: get_rev_reg_issued_details() ne dela. Mislim, da je bug v cloudcontroller kodi

- issue-vc: <s>pošiljanje offerja glede na proposal ne deluje..</s> <s>Težave s proposal - odstranjanje, ker načeloma nima smisla. Holder lahko prosi za offer prek basic message protokola!</s> Ja ampak, potem se holder ne more pritoževati na offer s proposal!

- <s>stestiraj present vp: pri tem je nujen proposal, ker drugače verifier sploh ne ve kaj lahko zahteva! Problem pri vp request, ker mora requester (verifier) že v requestu zahtevat točno določene parametre, kar ni problem, če je verifier tudi izdajatelj scheme in ve katere atribute zajema. Verifier, ki ne more pridit so scheme, neve za katere atribute naj prosi. Treba jih bo hardcodad. ALSO: razmisli še glede non_revoked parametra - nas zanima interval kdaj ali samo gledamo, da je trenutno veljavna?</s>

- <s>ko vzpostavim povezavo, agent z invitationom ne doseže drugega agenta - dodal sem trust ping in je v enem izmed primerov delovalo, stestiraj večkrat!! Zdaj sem v invitation dodal auto-accept in deluje basic message! Enkrat dela, drugič ne, zdaj sem odstranil multi_use pri invitation in dela!</s>

- <s>stestiraj še revocation skupaj z vp!</s>

- <s>ostal sem pri present-proof: send_pres_request_free ima names passan kot parameter - stestiraj! enako naredi še za non_revoked da vzame trenutni timestamp in enako za ostale funkcije!</s>

**02/04:**
- <s>dodaj v matching vc, da vzame vc z najvišjim cred_rev_id</s>
- razišči kje je težava s preverjanjem vp-ja, ko ponovno izdamo vc (trenutno se vp zapiše v cache tudi če ni veljaven) - reši težavo ali pa dodaj, da se vp izven agenta preveri na ledgerjuu preden se shrani v cache

**03/04:**
- <s>preimenuj cache.py ker ne gre dejansko za cache + uredi fajle</s>

**04/04:**
- opiši upravljanje universal in vcs kontrolerja