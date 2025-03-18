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
from services.wallet import (get_dids, create_did, get_public_did, assign_public_did)
from services.out_of_band import (create_invitation, receive_invitation)
from services.connections import get_connections
from services.did_exchange import (accept_invitation, accept_request)
from services.basic_message import send_message

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

        if command.lower() == "exit":
            print("Exiting CLI... ACA-Py controller will stop if you pressed ^C, otherwise it is still running.")
            stop_event.set()
            break
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
        elif command.startswith("connections"):
            try:
                result = await get_connections(client)
                conns_dict = result.to_dict()
                conns = conns_dict["results"]
                for c in conns:
                   print(c, "\n")
            except Exception as e:
                print(f"Error getting connections: {e}")
        elif command.startswith("message"):
            print("Enter connection ID:")
            try:
                conn_id = input()
                print("Enter message:")
                message = input()
                result = await send_message(client, conn_id, message)
                print(result)
            except Exception as e:
                print(f"Error sending message: {e}")       
        
        else:
            print("Unknown command. Try: invitation, connections")
        

# Main
if __name__ == "__main__":
    # Start the Quart app with asyncio loop
    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(app.run_task(host='0.0.0.0', port=5000))

    #loop = asyncio.new_event_loop()
    #asyncio.set_event_loop(loop)

    # Start CLI
    #loop.create_task(cli())  

    # Start the Quart webhook server with asyncio loop
    #loop.run_until_complete(app.run_task(host='0.0.0.0', port=5000, debug=True))
    asyncio.run(app.run_task(host='0.0.0.0', port=5050, debug=True))