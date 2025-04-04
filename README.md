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

**TODO**

### VCS controller

**TODO**

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