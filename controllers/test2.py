import asyncio
import json
import sys
import threading
from quart import Quart, request, jsonify
from aries_cloudcontroller import (
    AcaPyClient,
    InvitationCreateRequest,
    InvitationMessage,
    DIDCreate,
    DIDXRejectRequest,
    DIDResult
)

from utils.tools import (decode, extract_oob)
from services.wallet import (get_dids, create_did, get_public_did, assign_public_did, get_credential, get_credentials, delete_credential, get_revocation_status)
from services.out_of_band import (create_invitation, receive_invitation)
from services.connections import get_connections
from services.did_exchange import (accept_invitation, accept_request)
from services.basic_message import send_message
from services.schemas import (get_schemas, get_schema, publish_schema)
from services.credential_definitions import (get_cred_def, get_cred_defs, create_cred_def)
from services.revocation import (get_active_rev_reg, get_rev_reg_issued, get_rev_reg_issued_details, get_rev_regs, get_rev_reg, revoke)
from services.issue_credential import (send_proposal, send_offer, send_offer_free, send_request, issue_credential, report_problem, get_record, get_records, delete_record, store_credential)

app = Quart(__name__)

# Global controller (aca-py client)
client: AcaPyClient = None
#agent: AcaPyAgent = False
invitation_url = None

# Start up controller
@app.before_serving
async def startup():
    try:    
        global client
        client = AcaPyClient(
            base_url="http://localhost:8031",
            admin_insecure=True
        )
        print("Client created.")

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


# Webhook functions
async def process_create_invitation(client):
    try:
        result = await create_invitation(client)
        global invitation_url
        invitation_url = result.invitation_url
        print(f"Invitation created: {invitation_url}")
    except Exception as e:
        print(f"Error processing invitation creation: {e}")

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
        elif command.startswith("invitation"):
            print("Enter invitation URL:")
            try:
                url = input()
                encoded_invitation = extract_oob(url)
                decoded_invitation = decode(encoded_invitation)
                result = json.loads(decoded_invitation)  
                await receive_invitation(client, result)
            except Exception as e:
                print(f"Error processing invitation: {e}")

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

        # BASIC MESSAGE
        elif command.startswith("message"):
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
                print(f"Schema: {result.var_schema}")
            except Exception as e:
                print(f"Error getting schema: {e}")
        elif command.lower() == "publish schema":
            print("Enter list of schema attributes:")
            try:
                attributes = json.loads(input())
                print("Fetching current public DID...")
                res = await get_public_did(client)
                issuer_did = res["did"]
                print("Enter schema name:")
                schema_name = input()
                print("Enter schema version:")
                schema_version = input()
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
                connection_id = input()
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
                result = await get_records(client)
                print(f"Credential exchange records: {result}")
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
        elif command.lower() == "proposal":
            try:
                print("Enter connection ID:")
                conn_id = input()
                print("Enter schema name:")
                schema_name = input()
                result = await send_proposal(client, conn_id, schema_name)
                print(f"Credential proposal sent: {result}")
            except Exception as e:
                print(f"Error sending credential proposal: {e}")
        elif command.lower() == "offer":
            try:
                print("Type '0' for offer in reference to proposal or '1' for free offer:" )
                type = input()
                if type == "0":
                    public_did = await get_public_did(client)
                    issuer_id = public_did["did"]
                    print("Enter credential exchange ID:")
                    cred_ex_id = input()
                    print("Enter attributes list:")
                    attributes = input()
                    print("Enter credential definition ID:")
                    cred_def_id = input()
                    print("Enter schema ID:")
                    schema_id = input()
                    result = await send_offer(client, cred_ex_id, attributes, cred_def_id, issuer_id, schema_id)
                elif type == "1":
                    public_did = await get_public_did(client)
                    issuer_id = public_did["did"]
                    print("Enter connection ID:")
                    conn_id = input()
                    print("Enter attributes list:")
                    attributes = input()
                    print("Enter credential definition ID:")
                    cred_def_id = input()
                    print("Enter schema ID:")
                    schema_id = input()
                    result = await send_offer_free(client, conn_id, attributes, cred_def_id, issuer_id, schema_id)
                else:
                    print("Invalid offer")
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
        elif command.lower() == "problem":
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
                print(f"Stored credentials: {result}")
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

        else:
            print("Unknown command. Try: dids, create did, public did, assign did, invitation, connections, message, schemas, schema, publish schema, cred defs, cred def, create cred def, active rev reg, rev reg issued, rev reg issued details, rev regs, rev reg, revoke, proposal, vc record, vc records, delete vc record, offer, vc request, issue vc, store, problem, vcs, vc, rev status, delete vc")
        
# Main
if __name__ == "__main__":
    asyncio.run(app.run_task(host='0.0.0.0', port=5050, debug=True))