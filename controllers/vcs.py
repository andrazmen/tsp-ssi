import asyncio
import json
import os
import sys
import argparse
import importlib.util
from quart import Quart, request, jsonify
import urllib
from aries_cloudcontroller import (
    AcaPyClient
)

from authentication.x509_verification import (create_challenge, verify_sign, verify_cert)
from vcs.proof_handler import (get_proofs, handle_proof_delete, check_loop, check_ids)
from utils.tools import (decode, extract_oob)
from services.wallet import (get_dids, create_did, get_public_did, assign_public_did, get_did_endpoint, set_did_endpoint, get_credential, get_credentials, delete_credential, get_revocation_status)
from services.ledger import (register_nym)
from services.out_of_band import (create_invitation, receive_invitation, delete_invitation)
from services.connections import (get_connections, get_connection, get_metadata, set_metadata, delete_connection)
from services.trust_ping import send_ping
from services.did_exchange import (accept_invitation, accept_request)
from services.basic_message import send_message
from services.present_proof import (get_pres_record, get_pres_records, delete_pres_record, get_matching_credentials, send_presentation, send_pres_proposal, send_pres_request, send_pres_request_free, verify_presentation, report_pres_problem)

app = Quart(__name__)

# Global controller (aca-py client)
port = None
base_url = None
genesis = None
client: AcaPyClient = None
#agent: AcaPyAgent = False
invitation = None
invitation_url = None
challenge = None

def load_config(config_path):
    spec = importlib.util.spec_from_file_location("config", config_path)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    return config_module

# Start up controller
@app.before_serving
async def startup():
    try:    
        global client
        client = AcaPyClient(
            base_url=base_url,
            admin_insecure=True
        )
        print(f"Client created with base_url: {base_url}")

    except Exception as e:
        print(f"Error creating client: {e}")
        sys.exit(1)

    # Fetch genesis file
    print("Fetching genesis file...")
    asyncio.create_task(process_fetch_genesis(genesis))
    
# Serving controller
@app.while_serving
async def serving():
    print("Starting CLI...")
    
    stop_event = asyncio.Event()
    cli_task = asyncio.create_task(cli(stop_event))
    #task = loop.create_task(cli())  

    try:
       yield

    finally:
        print("Shutting down CLI...")
        stop_event.set()
        await cli_task
        print("CLI stopped.")
        #task.cancel()
        #try:
            #await task
        #except asyncio.CancelledError:
            #print("CLI task cancelled.")

# Shut down controller
@app.after_serving
async def shutdown():
    if client:
        await client.close()  
        print("Client closed.")

# Webhooks listeners
@app.route('/webhooks/topic/out_of_band/', methods=['POST'])
async def handle_oob_webhook():
    event_data = await request.get_json()
    print("Received OOB Webhook:", event_data, "\n")

    return jsonify({"status": "success"}), 200

@app.route('/webhooks/topic/connections/', methods=['POST'])
async def handle_conn_webhook():
    event_data = await request.get_json()
    print("Received Webhook Connection Event:", event_data, "\n")

    if event_data["state"] == "invitation" and event_data.get("rfc23_state") == "invitation-received":
        print("Invitation received!\n")

        if event_data["connection_protocol"] == "didexchange/1.1":
            print("Accepting invitation...\n")

            asyncio.create_task(process_invitation(event_data))

        else:
            print("Unknown connection protocol:", event_data["connection_protocol"], "\n")

    elif event_data["state"] == "request" and event_data.get("rfc23_state") == "request-received":
        print("Request received!\n")

        if event_data["connection_protocol"] == "didexchange/1.1":
            print("Accepting request...\n")

            asyncio.create_task(process_request(event_data))

        else:
            print("Unknown connection protocol:", event_data["connection_protocol"], "\n")

    print("Connection state:", event_data["state"], event_data.get("rfc23_state"), "\n")

    return jsonify({"status": "success"}), 200

@app.route('/webhooks/topic/connection_reuse_accepted/', methods=['POST'])
async def handle_reuse_connection_webhook():
    event_data = await request.get_json()
    print("Received Connection reuse Webhook:", event_data, "\n")

    return jsonify({"status": "success"}), 200

@app.route('/webhooks/topic/basicmessages/', methods=['POST'])
async def handle_basicmsg_webhook():
    event_data = await request.get_json()
    print("Received Message Webhook:", event_data, "\n")
    try:
        data = json.loads(event_data["content"])

        if data["type"] == "signature":
            if data["value"]:
                print("Received challenge signature:", data["value"], "\n")
                asyncio.create_task(process_signature(event_data["connection_id"], data))
        else:
            print("Received basic message:", event_data["content"], "\n")          
    except (json.JSONDecodeError, TypeError) as e: 
        print("Received basic message:", event_data["content"], "\n")  

    return jsonify({"status": "success"}), 200

@app.route('/webhooks/topic/problem_report/', methods=['POST'])
async def handle_problem_report_webhook():
    event_data = await request.get_json()
    print("Received problem report Webhook:", event_data, "\n")

    return jsonify({"status": "success"}), 200

@app.route('/webhooks/topic/present_proof_v2_0/', methods=['POST'])
async def handle_proof_webhook():
    event_data = await request.get_json()
    print("Received present proof Webhook:", event_data, "\n")

    if event_data["state"] == "proposal-received":
        pres_ex_id = event_data['pres_ex_id']
        proposal = event_data['by_format']
        print("Received vp proposal:", proposal, "with pres_ex_id:", pres_ex_id, "\n")

    elif event_data["state"] == "presentation-received":
        pres_ex_id = event_data['pres_ex_id']
        pres = event_data['by_format']
        print("Received vp presentation:", pres, "with pres_ex_id:", pres_ex_id, "\n")

    elif event_data["state"] == "done":
        if event_data["verified"] == "true":
            print("Presentation verified:", event_data, "sending challenge for certificate...\n")

            # Verify possible loop
            loop = await check_loop(client, event_data)
            if loop:
                print("The same Verifiable Presentation already exists in the system, deleting...\n")
                asyncio.create_task(handle_proof_delete(client, event_data))
                return jsonify({"status": "success"}), 200
            # Verify CN
            #metadata = await get_metadata(client, event_data["connection_id"])
            #metadata_dict = metadata.to_dict()
            #data = event_data["by_format"]["pres"]["anoncreds"]["requested_proof"]["revealed_attr_groups"]["auth_attr"]["values"]
            #if data.get("authorizee_cn", {}).get("raw") in metadata_dict["results"] or data.get("subject_cn", {}).get("raw") in metadata_dict["results"]:
            #    print("Metadata", metadata_dict["results"], "\n")
            #    print("Certificate with this CN already in metadata, skipping challenge...\n")
            #    return jsonify({"status": "success"}), 200

            #global challenge
            #challenge = asyncio.create_task(create_challenge(client, None, event_data, None))
            
            # Verify DID
            did = await check_ids(client, event_data)
            if not did:
                print("DID does not match with the one in the proof, deleting...\n")
                asyncio.create_task(handle_proof_delete(client, event_data))
                return jsonify({"status": "success"}), 200
            # Cache chain
            values = event_data["by_format"]["pres"]["anoncreds"]["requested_proof"]["revealed_attr_groups"]["auth_attr"]["values"]
            cn = values.get("authorizee_cn", {}).get("raw") or values.get("subject_cn", {}).get("raw")
            topic = values.get("topic", {}).get("raw") or values.get("cem_id", {}).get("raw")
            asyncio.create_task(check_proofs(client, event_data, cn, topic))
        elif event_data["verified"] == "false":
            print("Presentation verification failed:", event_data["pres_ex_id"], "deleting proof...\n")
            #asyncio.create_task(handle_proof_delete(client, event_data))
            values = event_data["by_format"]["pres"]["anoncreds"]["requested_proof"]["revealed_attr_groups"]["auth_attr"]["values"]
            cn = values.get("authorizee_cn", {}).get("raw") or values.get("subject_cn", {}).get("raw")
            topic = values.get("topic", {}).get("raw") or values.get("cem_id", {}).get("raw")
            asyncio.create_task(check_proofs(client, event_data, cn, topic))
        
    return jsonify({"status": "success"}), 200

# Access-control API
@app.route('/api/acs/', methods=['POST'])
async def handle_acs_api():
    try:
        event_data = await request.get_json()
        print("Received acs api request:", event_data)
        if event_data.get("id") and event_data.get("topic"):    
            id = event_data["id"]
            topic = event_data["topic"]

            proofs = await check_proofs(client, None, id, topic)

            print(f"Valid proofs: {proofs}", "\n")

            if proofs == {}:
                return jsonify(proofs), 404
            if proofs == None:
                return jsonify(), 500
            return jsonify(proofs), 200
        else:
            return jsonify({"error": "Bad Request"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start up functions
async def process_fetch_genesis(genesis_file_url):
    file_dir = os.path.dirname(os.path.realpath(__file__))
    target_local_path = f"{file_dir}/vcs/utils/genesis.txt"
    urllib.request.urlretrieve(genesis_file_url, target_local_path)
    return target_local_path

# Webhook functions
"""
async def process_create_invitation(client):
    try:
        inv = json.dumps(invitation)
        result = await create_invitation(client, inv)
        global invitation_url
        invitation_url = result.invitation_url
        print(f"Invitation created: {invitation_url}")
    except Exception as e:
        print(f"Error processing invitation creation: {e}")
"""
async def process_invitation(event_data):
    try:
        pub_did = await get_public_did(client)
        await accept_invitation(client, pub_did, event_data["connection_id"])
    except Exception as e:
        print(f"Error processing invitation: {e}")

async def process_request(event_data):
    try:
        await accept_request(client, event_data["connection_id"])

    except Exception as e:
        print(f"Error processing request: {e}") 

async def process_signature(conn_id, data):
    try:
        print("Verifying signature...\n")
        valid_sign = await verify_sign(client, conn_id, data, challenge)
        if not valid_sign:
            return False
        valid_cert = await verify_cert(data)
        if not valid_cert:
            return False
        print(f"Signature and chain are valid for certificate {cn}! Ready to send {data["cred_type"]} credential offer!","\n")
        return True

    except Exception as e:
        print(f"Error verifying signature: {e}")

# API functions
async def check_proofs(client, event_data, id, topic):
    try:
        #conns = await get_connections(client, state="active", their_did=did)
        #connection_id = conns.to_dict()["results"][0]["connection_id"]
        result = await get_pres_records(client, connection_id=None, role="verifier", state="done")

        #TEST
        with open("utils/tests/vcs-v2.json") as f:
            result = json.load(f)
        records = result["results"] 

        #records_dict = result.to_dict()
        #records = records_dict["results"]
        
        my_did = await get_public_did(client)

        result = await get_proofs(client, event_data, records, id, my_did["did"], topic)
        
        if result.get("revoked", {}) == True:
            print("No valid proofs, removing cache...", "\n")
            for _, proof in result.items():
                if proof == True or proof == False:
                    continue
                if proof.get("data").get("credential_type") == "authorization":
                    print("a")
                    #await delete_cached_get_proofs(get_proofs, requester_cn=proof.get("authorizee_cn"), topic=proof.get("data").get("topic"))
                    #await invalidate_cache(proof.get("authorizee_cn"), proof.get("data").get("topic"))
                if proof.get("data").get("credential_type") == "technical":
                    print("b")
                    #await delete_cached_get_proofs(get_proofs, requester_cn=proof.get("subject_cn"), topic=proof.get("data").get("cem_id"))
                    #await invalidate_cache(proof.get("subject_cn"), proof.get("data").get("cem_id"))
            return {}
        
        return result

    except Exception as e:
        print(f"Error checking proofs: {e}")      

# CLI
async def cli(stop_event: asyncio.Event):
    await asyncio.sleep(2)  
    print("\nType 'exit' to quit CLI.")
    
    while not stop_event.is_set():
        command = await asyncio.to_thread(input, "\n>>> ")

        # EXIT
        if command.lower() == "exit":
            print("Exiting CLI... ACA-Py controller will stop if you pressed ^C, otherwise it is still running.")
            stop_event.set()
            break

        # WALLET    
        elif command.startswith("dids"):
            try:
                result = await get_dids(client)
                for d in result:
                    print(d, "\n")
            except Exception as e:
                print(f"Error getting DIDs: {e}")
        elif command.startswith("create did"):
            print("local or public?")
            try:
                type = input()
                if type == "local":
                    method = "peer"
                    result = await create_did(client, method)
                elif type == "public":
                    method = "sov"
                    result = await create_did(client, method)
                print(result)
            except Exception as e:
                print(f"Error creating DID: {e}")
        elif command.startswith("register did"):
            try:
                print("Enter DID:")
                did = input()
                print("Enter verkey:")
                verkey = input()
                result = await register_nym(client, did, verkey)
                print(result)
            except Exception as e:
                print(f"Error registring DID: {e}")
        elif command.startswith("assign did"):
            print("Enter DID:")
            try:
                did = input()
                result = await assign_public_did(client, did)
                print(result)
            except Exception as e:
                print(f"Error assigning public DID: {e}")
        elif command.startswith("public did"):
            try:
                result = await get_public_did(client)
                print(result)
            except Exception as e:
                print(f"Error getting public DID: {e}")
        elif command.startswith("endpoint"):
            print("Enter DID:")
            try:
                did = input()
                result = await get_did_endpoint(client, did)
                print(result)
            except Exception as e:
                print(f"Error getting DID endpoint: {e}")
        elif command.startswith("set endpoint"):
            try:
                print("Enter DID:")
                did = input()
                print("Enter endpoint URL:")
                url = input()
                result = await set_did_endpoint(client, did, url)
                print(result)
            except Exception as e:
                print(f"Error setting DID endpoint: {e}")

        # OOB
        elif command.lower() == "url":
            try:
                print(invitation_url)
            except Exception as e:
                print(f"Error getting invitation url: {e}") 
        elif command.lower() == "create inv":
            try:
                inv = json.dumps(invitation)
                result = await create_invitation(client, inv)
                invitation_url = result.invitation_url
                print(f"Invitation created: {invitation_url}")
            except Exception as e:
                print(f"Error processing invitation creation: {e}")
        elif command.lower() == "delete inv":
            try:
                print("Enter invitation message ID:")
                inv_id = input()
                result = await delete_invitation(client, inv_id)
                print(f"Invitation removed: {result}")
            except Exception as e:
                print(f"Error processing invitation creation: {e}")
        elif command.startswith("receive inv"):
            print("Enter invitation URL:")
            try:
                url = input() 
                await receive_invitation(client, url)
            except Exception as e:
                print(f"Error processing invitation: {e}")

        # DIDX
        elif command.lower() == "accept inv":
            try:
                public_did = await get_public_did(client)
                print("Enter connection ID:")
                connection_id = input()
                result = await accept_invitation(client, public_did, connection_id)
                print(f"Invitation accepted: {result}")
            except Exception as e:
                print(f"Error accepting invitation: {e}")
        elif command.lower() == "accept didx req":
            try:
                print("Enter connection ID:")
                connection_id = input()
                result = await accept_request(client, connection_id)
                print(f"DIDx request accepted: {result}")
            except Exception as e:
                print(f"Error accepting DIDx request: {e}")
        elif command.lower() == "reject didx":
            try:
                print("Enter connection ID:")
                connection_id = input()
                print("Enter reason for rejection:")
                description = input()
                result = await reject(client, connection_id, description)
                print(f"DIDx rejected: {result}")
            except Exception as e:
                print(f"Error rejecting DIDx: {e}")
        
        # CONNECTIONS
        elif command.startswith("conns"):
            try:
                print("Enter connection state:")
                conn_state = input()
                if conn_state:
                    state = conn_state
                else:
                    state = None
                print("Enter their DID:")
                did = input()
                if did:
                    their_did = did
                else:
                    their_did = None
                result = await get_connections(client, state, their_did)
                conns_dict = result.to_dict()
                conns = conns_dict["results"]
                for c in conns:
                   print(c, "\n")
            except Exception as e:
                print(f"Error getting connections: {e}")
        elif command.lower() == "conn":
            try:
                print("Enter connection ID:")
                conn_id = input()
                result = await get_connection(client, conn_id)
                print(f"Connection record for connection {conn_id}: {result.to_dict()}")
            except Exception as e:
                print(f"Error getting connection: {e}")   
        elif command.lower() == "conn metadata":
            try:
                print("Enter connection ID:")
                conn_id = input()
                result = await get_metadata(client, conn_id)
                print(f"Metadata for connection {conn_id}: {result.to_dict()}")
            except Exception as e:
                print(f"Error getting metadata: {e}")
        elif command.lower() == "set conn metadata":
            try:
                print("Enter connection ID:")
                conn_id = input()
                print("Enter certificate CN:")
                certificate_cn = input()
                result = await set_metadata(client, conn_id, certificate_cn)
                print(f"Metadata for connection {conn_id} set: {result}")
            except Exception as e:
                print(f"Error setting metadata: {e}")
        elif command.lower() == "delete conn":
            try:
                print("Enter connection ID:")
                connection_id = input()
                result = await delete_connection(client, connection_id)
                print(f"Connection record for connection {connection_id} deleted: {result}")
            except Exception as e:
                print(f"Error deleting connection: {e}")         
        
        # TRUST PING
        elif command.lower() == "ping":
            try:
                print("Enter connection ID:")
                connection_id = input()
                print("Enter comment:")
                comment = input()
                result = await send_ping(client, connection_id, comment)
                print("Ping sent:", result)
            except Exception as e:
                print(f"Error sending ping: {e}")

        # BASIC MESSAGE
        elif command.lower() == "message":
            print("Enter connection ID:")
            try:
                conn_id = input()
                print("Enter message:")
                message = input()
                result = await send_message(client, conn_id, message)
                print("Message sent:", result)
            except Exception as e:
                print(f"Error sending message: {e}")
        
        ## PRESENT VP
        elif command.lower() == "vp record":
            try:
                print("Enter presentation exchange ID:")
                pres_ex_id = input()
                result = await get_pres_record(client, pres_ex_id)
                result_dict = result.to_dict()
                print(f"Presentation exchange record: {result_dict}")
            except Exception as e:
                print(f"Error getting presentation exchange record: {e}")
        elif command.lower() == "vp records":
            try:
                print("Enter connection ID:")
                conn_id = input()
                if conn_id:
                    connection_id = conn_id
                else:
                    connection_id = None
                print("Enter presentation exchange state (proposal-sent/proposal-received/request-sent/request-received/presentation-sent/presentation-received/done/abandoned):")
                pres_ex_state = input()
                if pres_ex_state:
                    state = pres_ex_state
                else:
                    state = None
                print("Enter your role in presentation exchange record (issuer/holder):")
                pres_ex_role = input()
                if pres_ex_role:
                    role = pres_ex_role
                else:
                    role = None
                result = await get_pres_records(client, connection_id, role, state)
                records_dict = result.to_dict()
                records = records_dict["results"]
                for r in records:
                   print(f"Presentation exchange record {r["pres_ex_id"]}:\n{r}\n")
            except Exception as e:
                print(f"Error getting presentation exchange records: {e}")
        elif command.lower() == "delete vp record":
            try:
                print("Enter presentation exchange ID:")
                pres_ex_id = input()
                result = await delete_pres_record(client, pres_ex_id)
                print(f"Presentation exchange record deleted: {result}")
            except Exception as e:
                print(f"Error deleting presentation exchange record: {e}")
        elif command.lower() == "vp problem":
            try:
                print("Enter presentation exchange ID:")
                pres_ex_id = input()
                print("Enter report description:")
                description = input()
                result = await report_pres_problem(client, pres_ex_id, description)
                print(f"Problem report sent: {result}")
            except Exception as e:
                print(f"Error sending problem report: {e}")
        elif command.lower() == "vp request":
            try:
                print("Type '0' for request in reference to proposal or '1' for free request:" )
                type = input()
                if type == "0":
                    print("Enter presentation exchange ID:")
                    pres_ex_id = input()
                    result = await send_pres_request(client, pres_ex_id)
                    result_dict = result.to_dict()
                    print(f"Request sent: {result_dict}")
                elif type == "1":
                    print("Enter connection ID:")
                    connection_id = input()
                    print("Enter schema name:")
                    schema_name = input()
                    print("Enter attributes list:")
                    names = json.loads(input())
                    result = await send_pres_request_free(client, connection_id, names, schema_name)
                    result_dict = result.to_dict()
                    print(f"Request sent: {result_dict}")
                else:
                    print("Invalid request")
            except Exception as e:
                print(f"Error sending request: {e}")
        elif command.lower() == "verify":
            try:
                print("Enter presentation exchange ID:")
                pres_ex_id = input()
                result = await verify_presentation(client, pres_ex_id)
                result_dict = result.to_dict()
                print(f"Presentation verified: {result_dict}")
                if result_dict["verified"] == True:
                    print("Verifying certificate...")
                    certificate_cn = verify_cn(client, result_dict)
                    if certificate_cn:
                        print("Certificate invalid, setting connection metadata...")
                        conn_id = result_dict.get("connection_id")
                        result = await set_metadata(client, conn_id, certificate_cn)
                        print(f"Metadata for connection {conn_id} set: {result}")
            except Exception as e:
                print(f"Error verifying presentation: {e}")

        ## PROOFS
        elif command.lower() == "proofs":
            try:
                result = await get_pres_records(client, connection_id=None, role="verifier", state="done")
                records_dict = result.to_dict()
                records = records_dict["results"]
                print("Stored proofs:")
                for r in records:
                    proof = {}
                    proof["pres_ex_id"] = r["pres_ex_id"]
                    proof["connection_id"] = r["connection_id"]
                    proof["data"] = r["by_format"]["pres"]["anoncreds"]["requested_proof"]
                    print(proof, "\n")
            except Exception as e:
                print(f"Error fetching stored proofs: {e}")            

        else:
            print("Unknown command. Try: dids, create did, public did, register did, assign did, endpoint, set endpoint, url, create inv, receive inv, accept inv, delete inv, accept didx req, reject didx, conns, conn, conn metadata, set conn metadata, delete conn, ping, message, vp records, vp record, delete vp record, vp problem, vp request, verify, proofs")
        
# Main
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the universal controller with a custom config file.")
    parser.add_argument("--config", type=str, required=True, help="Path to the Python config file.")

    args = parser.parse_args()
    
    config = load_config(args.config)
    
    base_url = config.BASE_URL
    port = config.PORT
    schema_attr_conf = config.SCHEMA_ATTR
    schema_name_conf = config.SCHEMA_NAME
    schema_version_conf = config.SCHEMA_VERSION
    invitation = config.INVITATION
    genesis = config.GENESIS
    
    asyncio.run(app.run_task(host='0.0.0.0', port=port, debug=True))