import asyncio
import json
import sys
import argparse
import importlib.util
from quart import Quart, request, jsonify
from aries_cloudcontroller import (
    AcaPyClient
)

from vcs.cache import (cache_proof, get_proof, validate_proof)
from utils.tools import (decode, extract_oob)
from services.wallet import (get_dids, create_did, get_public_did, assign_public_did, get_credential, get_credentials, delete_credential, get_revocation_status)
from services.out_of_band import (create_invitation, receive_invitation, delete_invitation)
from services.connections import get_connections
from services.trust_ping import send_ping
from services.did_exchange import (accept_invitation, accept_request)
from services.basic_message import send_message
from services.present_proof import (get_pres_record, get_pres_records, delete_pres_record, get_matching_credentials, send_presentation, send_pres_proposal, send_pres_request, send_pres_request_free, verify_presentation, report_pres_problem)

app = Quart(__name__)

# Global controller (aca-py client)
port = None
base_url = None
client: AcaPyClient = None
#agent: AcaPyAgent = False
invitation = None
invitation_url = None

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

    # Create public invitation
    #print("Creating public invitation...")
    #asyncio.create_task(process_create_invitation(client))
    
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

    if event_data["state"] == "invitation" and event_data["rfc23_state"] == "invitation-received":
        print("Invitation received!\n")

        if event_data["connection_protocol"] == "didexchange/1.1":
            print("Accepting invitation...\n")

            asyncio.create_task(process_invitation(event_data))

        else:
            print("Unknown connection protocol:", event_data["connection_protocol"], "\n")

    elif event_data["state"] == "request" and event_data["rfc23_state"] == "request-received":
        print("Request received!\n")

        if event_data["connection_protocol"] == "didexchange/1.1":
            print("Accepting request...\n")

            asyncio.create_task(process_request(event_data))

        else:
            print("Unknown connection protocol:", event_data["connection_protocol"], "\n")

    print("Connection state:", event_data["state"], event_data["rfc23_state"], "\n")

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

    print("Message received:", event_data["content"], "\n")

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

    if event_data["state"] == "done":
        if event_data["role"] == "verifier":
            if event_data["verified"] == "true":
                proof_id = event_data["pres_ex_id"]
                conn_id = event_data["connection_id"]
                data = event_data["by_format"]["pres"]["anoncreds"]["requested_proof"]

                cache_proof(proof_id, conn_id, data)

    return jsonify({"status": "success"}), 200

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
        elif command.startswith("invitation"):
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
        
        # CONNECTIONS
        elif command.startswith("connections"):
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
                print(f"Presentation exchange record: {result}")
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
                   print(r, "\n")
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
        elif command.lower() == "matching vc":
            try:
                print("Enter presentation exchange ID:")
                pres_ex_id = input()
                result = await get_matching_credentials(client, pres_ex_id)
                print(f"Matching credentials: {result}")
            except Exception as e:
                print(f"Error getting matching credentials: {e}")
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
        elif command.lower() == "send vp":
            try:
                print("Enter presentation exchange ID:")
                pres_ex_id = input()
                print("Enter credential ID:")
                cred_id = input()
                result = await send_presentation(client, pres_ex_id, cred_id)
                print(f"Presentation sent: {result}")
            except Exception as e:
                print(f"Error sending presentation: {e}")
        elif command.lower() == "vp proposal":
            try:
                print("Enter connection ID:")
                connection_id = input()
                print("Enter schema name:")
                schema_name = input()
                print("Enter attributes list:")
                names = json.loads(input())
                result = await send_pres_proposal(client, connection_id, names, schema_name)
                print(f"Presentation proposal sent: {result}")
            except Exception as e:
                print(f"Error sending presentation proposal: {e}")
        elif command.lower() == "vp request":
            try:
                print("Type '0' for request in reference to proposal or '1' for free request:" )
                type = input()
                if type == "0":
                    print("Enter presentation exchange ID:")
                    pres_ex_id = input()
                    result = await send_pres_request(client, pres_ex_id)
                    print(f"Request sent: {result}")
                elif type == "1":
                    print("Enter connection ID:")
                    connection_id = input()
                    print("Enter schema name:")
                    schema_name = input()
                    print("Enter attributes list:")
                    names = json.loads(input())
                    result = await send_pres_request_free(client, connection_id, names, schema_name)
                    print(f"Request sent: {result}")
                else:
                    print("Invalid request")
            except Exception as e:
                print(f"Error sending request: {e}")
        elif command.lower() == "verify":
            try:
                print("Enter presentation exchange ID:")
                pres_ex_id = input()
                result = await verify_presentation(client, pres_ex_id)
                print(f"Presentation verified: {result}")
            except Exception as e:
                print(f"Error verifying presentation: {e}")

        else:
            print("Unknown command. Try: dids, create did, public did, assign did, url, invitation, accept inv, accept didx req, connections, ping, message, schemas, schema, publish schema, cred defs, cred def, create cred def, active rev reg, rev reg issued, rev reg issued details, rev regs, rev reg, revoke, vc record, vc records, delete vc record, offer, vc request, issue vc, store, vc problem, vcs, vc, rev status, delete vc, vp records, vp record, delete vp record, matching vc, vp problem, send vp, vp proposal, vp request, verify")
        
# Main
if __name__ == "__main__":
    #asyncio.run(app.run_task(host='0.0.0.0', port=port, debug=True))

    parser = argparse.ArgumentParser(description="Run the universal controller with a custom config file.")
    parser.add_argument("--config", type=str, required=True, help="Path to the Python config file.")

    args = parser.parse_args()
    
    config = load_config(args.config)
    
    base_url = config.base_url
    port = config.port
    schema_attr_conf = config.schema_attr
    schema_name_conf = config.schema_name
    schema_version_conf = config.schema_version
    invitation = config.invitation
    
    asyncio.run(app.run_task(host='0.0.0.0', port=port, debug=True))