import asyncio
import json
import sys
import argparse
import importlib.util
from quart import Quart, request, jsonify
from aries_cloudcontroller import (
    AcaPyClient
)

from utils.tools import (decode, extract_oob)
from services.wallet import (get_dids, create_did, get_public_did, assign_public_did, get_credential, get_credentials, delete_credential, get_revocation_status)
from services.out_of_band import (create_invitation, receive_invitation, delete_invitation)
from services.connections import get_connections
from services.trust_ping import send_ping
from services.did_exchange import (accept_invitation, accept_request)
from services.basic_message import send_message
from services.schemas import (get_schemas, get_schema, publish_schema)
from services.credential_definitions import (get_cred_def, get_cred_defs, create_cred_def)
from services.revocation import (get_active_rev_reg, get_rev_reg_issued, get_rev_reg_issued_details, get_rev_regs, get_rev_reg, revoke, check_revocation_status)
from services.issue_credential import (send_offer_free, send_request, issue_credential, report_problem, get_record, get_records, delete_record, store_credential)
from services.present_proof import (get_pres_record, get_pres_records, delete_pres_record, get_matching_credentials, send_presentation, send_pres_proposal, send_pres_request, send_pres_request_free, verify_presentation, report_pres_problem)

app = Quart(__name__)

# Global controller (aca-py client)
port = None
base_url = None
client: AcaPyClient = None
#agent: AcaPyAgent = False
invitation_conf = None
invitation_url = None
schema_name_conf = None
schema_version_conf = None
schema_attr_conf = None

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

@app.route('/webhooks/topic/issue_credential_v2_0/', methods=['POST'])
async def handle_credential_webhook():
    event_data = await request.get_json()
    print("Received VC Webhook:", event_data, "\n")

    if event_data["state"] == "offer-received":
        cred_ex_id = event_data['cred_ex_id']
        offer = event_data['cred_offer']
        print("Received VC offer:", offer['credential_preview'], "with cred_ex_id:", cred_ex_id, "\n")
    elif event_data["state"] == "credential-received":
        cred_ex_id = event_data['cred_ex_id']
        print("Received VC:", event_data, "with cred_ex_id:", cred_ex_id, "\n")
    elif event_data["state"] == "credential-issued":
        cred_ex_id = event_data['cred_ex_id']
        print("Issued VC:", event_data, "with cred_ex_id:", cred_ex_id, "\n")

    return jsonify({"status": "success"}), 200

@app.route('/webhooks/topic/issue_credential_v2_0_anoncreds/', methods=['POST'])
async def handle_anonCreds_credential_webhook():
    event_data = await request.get_json()
    print("Received AnonCreds VC Webhook:", event_data, "\n")

    return jsonify({"status": "success"}), 200

@app.route('/webhooks/topic/issuer_cred_rev/', methods=['POST'])
async def handle_revocation_webhook():
    event_data = await request.get_json()
    print("Received revocation Webhook:", event_data, "\n")

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
    elif event_data["state"] == "request-received":
        pres_ex_id = event_data['pres_ex_id']
        print("Received vp request:", event_data, "with pres_ex_id:", pres_ex_id, "\n")
    elif event_data["state"] == "presentation-received":
        pres_ex_id = event_data['pres_ex_id']
        print("Received vp:", event_data, "with pres_ex_id:", pres_ex_id, "\n")
        
    return jsonify({"status": "success"}), 200

@app.route('/webhooks/topic/revocation-notification/', methods=['POST'])
async def handle_rev_notif_webhook():
    event_data = await request.get_json()
    print("Received revocation notification Webhook:", event_data, "\n")

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
                inv = json.dumps(invitation_conf)
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

        # SCHEMA    
        elif command.lower() == "schemas":
            try:
                print("Enter schema issuer DID:")
                did = input()
                if did:
                    schema_issuer_did = did
                else:
                    schema_issuer_did = None
                print("Enter schema name:")
                name = input()
                if name:
                    schema_name = name
                else:
                    schema_name = None
                print("Enter schema version:")
                version = input()
                if version:
                    schema_version = version
                else:
                    schema_version = None
                result = await get_schemas(client, schema_issuer_did, schema_name, schema_version)
                print("\n", result)
            except Exception as e:
                print(f"Error getting schemas: {e}")
        elif command.lower() == "schema":
            print("Enter schema ID:")
            try:
                schema_id = input()
                result = await get_schema(client, schema_id)
                print(f"Schema: {result}")
            except Exception as e:
                print(f"Error getting schema: {e}")
        elif command.lower() == "publish schema":
            try:
                print("Fetching current public DID...")
                res = await get_public_did(client)
                issuer_did = res["did"]
                print("Enter schema name (if None, default config schema name!):")
                name = input()
                if name:
                    schema_name = name
                else:
                    schema_name = schema_name_conf
                print("Enter schema version (if None, default config schema version!):")
                version = input()
                if version:
                    schema_version = version
                else:
                    schema_version = schema_version_conf
                print("Enter list of schema attributes (if None, default config schema attributes!):")
                attr_json = input()
                if attr_json:
                    attributes = json.loads(attr_json)
                else:
                    attributes = schema_attr_conf
                result = await publish_schema(client, issuer_did, attributes, schema_name, schema_version)
                print(f"Schema created: {result}")
            except Exception as e:
                print(f"Error publishing schema: {e}")   

        # CREDENTIAL DEFINITION
        elif command.lower() == "cred defs":
            try:
                print("Enter issuer DID:")
                did = input()
                if did:
                    issuer_id = did
                else:
                    issuer_id = None
                print("Enter schema ID:")
                id = input()
                if id:
                    schema_id = id
                else:
                    schema_id = None
                print("Enter schema name:")
                name = input()
                if name:
                    schema_name = name
                else:
                    schema_name = None
                print("Enter schema version:")
                version = input()
                if version:
                    schema_version = version
                else:
                    schema_version = None
                result = await get_cred_defs(client, issuer_id, schema_id, schema_name, schema_version)
                print(f"Credential definitions: {result}")
            except Exception as e:
                print(f"Error getting credential definitions: {e}")
        elif command.lower() == "cred def":
            print("Enter credential definition ID:")
            try:
                cred_def_id = input()
                result = await get_cred_def(client, cred_def_id)
                print(f"Credential definition: {result}")
            except Exception as e:
                print(f"Error getting credential definition: {e}")
        elif command.lower() == "create cred def":
            try:
                print("Fetching current public DID...")
                res = await get_public_did(client)
                issuer_id = res["did"]
                print("Enter schema ID:")
                schema_id = input()
                result = await create_cred_def(client, issuer_id, schema_id)
                print(f"Credential definition created: {result}")
            except Exception as e:
                print(f"Error creating credential definition: {e}")
        
        # REVOCATION
        elif command.lower() == "active rev reg":
            try:
                print("Enter credential definition ID:")
                cred_def_id = input()
                result = await get_active_rev_reg(client, cred_def_id)
                print(f"Active revocation registry: {result}")
            except Exception as e:
                print(f"Error getting active revocation registry: {e}")
        elif command.lower() == "rev reg issued":
            try:
                print("Enter revocation registry ID:")
                rev_reg_id = input()
                result = await get_rev_reg_issued(client, rev_reg_id)
                print(f"Number of issued credentials : {result}")
            except Exception as e:
                print(f"Error getting number of issued credentials: {e}")
        elif command.lower() == "rev reg issued details":
            try:
                print("Enter revocation registry ID:")
                rev_reg_id = input()
                result = await get_rev_reg_issued_details(client, rev_reg_id)
                print(f"Details of issued credentials : {result}")
            except Exception as e:
                print(f"Error getting details of issued credentials: {e}")
        elif command.lower() == "rev regs":
            try:
                print("Enter credential definition ID:")
                cred_def_id = input()
                result = await get_rev_regs(client, cred_def_id)
                print(f"Revocation registries : {result}")
            except Exception as e:
                print(f"Error getting revocation registries: {e}")
        elif command.lower() == "rev reg":
            try:
                print("Enter revocation registry ID:")
                rev_reg_id = input()
                result = await get_rev_reg(client, rev_reg_id)
                print(f"Revocation registry : {result}")
            except Exception as e:
                print(f"Error getting revocation registry: {e}")
        elif command.lower() == "revoke":
            try:
                print("Enter connection ID:")
                conn_id = input()
                print("Enter credential exchange ID:")
                cred_ex_id = input()
                print("Enter thread ID:")
                thread_id = input()
                print("Enter comment:")
                comment = input()
                result = await revoke(client, comment, conn_id, cred_ex_id, thread_id)
                print(f"Credential revoked: {result}")
            except Exception as e:
                print(f"Error revoking credential: {e}")

        # ISSUE VC
        elif command.lower() == "vc records":
            try:
                print("Enter connection ID:")
                conn_id = input()
                if conn_id:
                    connection_id = conn_id
                else:
                    connection_id = None
                print("Enter credential exchange state (proposal-sent/proposal-received/offer-sent/offer-received/request-sent/request-received/credential-issued/credential-received/done/credential-revoked/abandoned):")
                cred_ex_state = input()
                if cred_ex_state:
                    state = cred_ex_state
                else:
                    state = None
                print("Enter your role in credential exchange record (issuer/holder):")
                cred_ex_role = input()
                if cred_ex_role:
                    role = cred_ex_role
                else:
                    role = None
                result = await get_records(client, connection_id, role, state)
                records_dict = result.to_dict()
                records = records_dict["results"]
                for r in records:
                   print(r, "\n")
            except Exception as e:
                print(f"Error getting credential exchange records: {e}")
        elif command.lower() == "vc record":
            try:
                print("Enter credential exchange ID:")
                cred_ex_id = input()
                result = await get_record(client, cred_ex_id)
                print(f"Credential exchange record: {result}")
            except Exception as e:
                print(f"Error gettting credential exchange record: {e}")
        elif command.lower() == "delete vc record":
            try:
                print("Enter credential exchange ID:")
                cred_ex_id = input()
                result = await delete_record(client, cred_ex_id)
                print(f"Credential exchange record deleted: {result}")
            except Exception as e:
                print(f"Error deleting credential exchange record: {e}")
        elif command.lower() == "offer":
            try:
                public_did = await get_public_did(client)
                issuer_id = public_did["did"]
                print("Enter connection ID:")
                conn_id = input()
                print("Enter attributes json:")
                attributes = input()
                print("Enter credential definition ID:")
                cred_def_id = input()
                print("Enter schema ID:")
                schema_id = input()
                result = await send_offer_free(client, conn_id, attributes, cred_def_id, issuer_id, schema_id)
            except Exception as e:
                print(f"Error sending credential offer: {e}")
        elif command.lower() == "vc request":
            try:
                public_did = await get_public_did(client)
                holder_did = public_did["did"]
                print("Enter credential exchange ID:")
                cred_ex_id = input()
                result = await send_request(client, cred_ex_id, holder_did)
                print(f"Credential request sent: {result}")
            except Exception as e:
                print(f"Error sending credential request: {e}")
        elif command.lower() == "issue vc":
            try:
                print("Enter credential exchange ID:")
                cred_ex_id = input()
                result = await issue_credential(client, cred_ex_id)
                print(f"Credential issued: {result}")
            except Exception as e:
                print(f"Error issuing credential: {e}")
        elif command.lower() == "store":
            try:
                print("Enter credential exchange ID:")
                cred_ex_id = input()
                result = await store_credential(client, cred_ex_id)
                print(f"Credential stored: {result}")
            except Exception as e:
                print(f"Error storing credential: {e}")
        elif command.lower() == "vc problem":
            try:
                print("Enter credential exchange ID:")
                cred_ex_id = input()
                print("Enter report description:")
                description = input()
                result = await report_problem(client, cred_ex_id, description)
                print(f"Problem report sent: {result}")
            except Exception as e:
                print(f"Error sending problem report: {e}")
        
        ## VC
        elif command.lower() == "vcs":
            try:
                result = await get_credentials(client)
                print(f"Stored credentials:", "\n")
                for vc in result:
                    print(vc, "\n")
            except Exception as e:
                print(f"Error getting stored credentials: {e}")
        elif command.lower() == "vc":
            try:
                print("Enter credential ID:")
                cred_id = input()
                result = await get_credential(client, cred_id)
                print(f"Stored credential: {result}")
            except Exception as e:
                print(f"Error getting stored credential: {e}")
        elif command.lower() == "rev status":
            try:
                print("Enter credential ID:")
                cred_id = input()
                result = await get_revocation_status(client, cred_id)
                print(f"Credential revocation status: {result}")
            except Exception as e:
                print(f"Error getting credential revocation status: {e}")
        elif command.lower() == "delete vc":
            try:
                print("Enter credential ID:")
                cred_id = input()
                result = await delete_credential(client, cred_id)
                print(f"Stored credential deleted: {result}")
            except Exception as e:
                print(f"Error deleting stored credential: {e}")
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
                print(f"Matching credentials: {result}", "\n")
                print("Credential ID:", result[0].cred_info.referent)
                print("Credential revocation ID:", result[0].cred_info.cred_rev_id)
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
                print("Credential revocation ID:")
                cred_rev_id = input()
                result = await send_presentation(client, pres_ex_id, cred_id, cred_rev_id)
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

        elif command.lower() == "rev":
            try:
                print("Enter rev reg ID:")
                rev_reg_id = input()
                result = await check_revocation_status(client, rev_reg_id)
                print(f"Rev reg: {result}")
            except Exception as e:
                print(f"Error: {e}")

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
    invitation_conf = config.invitation
    
    asyncio.run(app.run_task(host='0.0.0.0', port=port, debug=True))