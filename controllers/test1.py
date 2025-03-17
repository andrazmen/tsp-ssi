import asyncio
import json
from quart import Quart, request, jsonify
from aries_cloudcontroller import (
    AcaPyClient,
    InvitationCreateRequest,
    InvitationMessage,
    DIDCreate,
    DIDXRejectRequest,
    DIDResult
)

app = Quart(__name__)

# Global ACA-Py client (initialized in startup hook)
client: AcaPyClient = None

# ✅ Initialize ACA-Py client inside an async startup function
@app.before_serving
async def startup():
    global client
    client = AcaPyClient(
        base_url="http://localhost:8021",
        admin_insecure=True
    )

@app.after_serving
async def shutdown():
    await client.close()  # ✅ Properly close ACA-Py client when shutting down

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
            print("Accepting request...\n")

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

async def process_invitation(event_data):
    try:
        pub_did = await get_public_did()
        await accept_invitation(pub_did, event_data["connection_id"])
    except Exception as e:
        print(f"Error processing invitation: {e}")

async def process_request(event_data):
    try:
        await accept_request(event_data["connection_id"])

    except Exception as e:
        print(f"Error processing request: {e}")


async def get_connections(
    alias=None,
    connection_protocol=None,
    invitation_key=None,
    invitation_msg_id=None,
    limit=None,
    my_did=None,
    offset=None,
    state=None,
    their_did=None,
    their_public_did=None,
    their_role=None
):
    result = await client.connection.get_connections(
        alias=alias,
        connection_protocol=connection_protocol,
        invitation_key=invitation_key,
        invitation_msg_id=invitation_msg_id,
        limit=limit,
        my_did=my_did,
        offset=offset,
        state=state,
        their_did=their_did,
        their_public_did=their_public_did,
        their_role=their_role
    )

    print(result)

async def get_public_did():
    result = await client.wallet.get_public_did()

    return result

async def receive_invitation(invitation_msg):
    inv_msg = InvitationMessage.from_dict(invitation_msg)
    result = await client.out_of_band.receive_invitation(
        #alias,
        #auto-accept,
        #mediation_id,
        #use_existing_connection
        body=inv_msg
    )

    print(result)

async def accept_invitation(public_did, connection_id):
    result = await client.did_exchange.accept_invitation(
        conn_id = connection_id,
        use_did = public_did.result.did
    )
    print(result)

async def accept_request(connection_id):
    result = await client.did_exchange.accept_request(
        conn_id = connection_id,
        #mediation_id,
        #my_endpoint,
        use_public_did = True
    )

    print(result)

async def cli():
    await asyncio.sleep(2)  # Ensure Quart is up before CLI starts
    print("\nType 'exit' to quit.")
    while True:
        command = input("\n>>> ").strip()

        if command.lower() == "exit":
            print("Exiting CLI...")
            break
        elif command.startswith("invitation"):
            print("Enter invitation message (JSON):")
            try:
                json_data = input()
                result = json.loads(json_data)  
                await receive_invitation(result)
            except Exception as e:
                print(f"Error processing invitation: {e}")
        else:
            print("Unknown command. Try: invitation")

if __name__ == "__main__":
    # Start the Quart app with asyncio loop
    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(app.run_task(host='0.0.0.0', port=5000))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.create_task(cli())  # Start CLI
    loop.run_until_complete(app.run_task(host='0.0.0.0', port=5000, debug=True))