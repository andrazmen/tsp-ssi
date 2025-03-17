## TODO:
- <s>dodaj da se invitation nardi ob zagonu</s>
- <s>dodaj webserver za webhooke</s>
- dodaj v test1.py da bo agent tekel in poslušal vse možne akcije
- ideja: dodaj, da se ročno poda funkciji receive-invitation invitation_url
- <s>dodaj, da bo poslušal webhook connection, da se bo izvedel spodnji flow:

1. Ob zagonu: create multi-use invitation (iz tega se kreira id oz. invitation_msg_id) (to se lahko naredi tudi z --invite,--invite-label, --invite-multi-use, --invite-public, --invite-metadata-json ob zagonu agenta). Smiselno, ker imajo na ta način vsi narejen URL, prek katerega se lahko povezujejo drugi. Vprašanje je potem samo, kako ti pridejo do tega url-ja
2. posluša webhooke:
- TODO: kako dobi invitation iz URL
- (ko prejme invitation z out-of-band/receive-invitation) v primeru, da pride v connections: state="invitation", their_role="inviter", connection_protocol="didexchange1.1", invitation_msg_id=(id iz 1. točke) se sproži POST didexchange/{conn_id}/accept-invitation (potrebuje conn_id in use_did (trenutni javni DID), ki ga dobi z GET wallet/did/public)
</s> Manjka samo kako passat invitation URL, torej /out-of-band/receive-invitation

import subprocess
import time
import signal
import sys
import asyncio
#from flask import Flask, request, jsonify
from quart import Quart, request, jsonify

from aries_cloudcontroller import (
    AcaPyClient,
    ConnRecord,
    CreateInvitationRequest,
    InvitationResult,
    ReceiveInvitationRequest,
    InvitationCreateRequest,
    InvitationMessage,
    DIDCreate,
    DIDXRejectRequest
)
app = Quart(__name__)

@app.route('/webhooks/topic/out_of_band/', methods=['POST'])
async def handle_oob_webhook():
    event_data = await request.get_json()
    print("Received Webhook Event:", event_data)
        
    # Process the webhook event (e.g., log it, store it, trigger actions)
    return jsonify({"status": "success"}), 200

@app.route('/webhooks/topic/connections/', methods=['POST'])
async def handle_conn_webhook():
    event_data = await request.get_json()
    print("Received Webhook Connection Event:", event_data)

    if event_data["state"] == "invitation" and event_data["rfc23_state"] == "invitation-received":
        print("Invitation received!")

        if event_data["connection_protocol"] == "didexchange/1.1":
            print("Accepting invitation...")

            result = await client.wallet.get_public_did()

            res = await client.did_exchange.accept_invitation(
                conn_id = event_data["connection_id"],
                #my_endpoint,
                #my_label,
                use_did = result.did,
                #use_did_method
            )

            print(res)


            # KAKO KLICAT TE FUNKCIJE????
            #pub_did = await get_public_did()
            #await accept_invitation(pub_did, event_data["connection_id"])
        else:
            print("Unknown connection protocol:", event_data["connection_protocol"])
        
    # Process the webhook event (e.g., log it, store it, trigger actions)
    return jsonify({"status": "success"}), 200

def start_webhook():
    server = app.run(host='0.0.0.0', port=5000, debug=True)

    return server

client = AcaPyClient(
    base_url="http://localhost:8021",
    #api_key="myApiKey"
    admin_insecure=True
)

## OUT-OF-BAND
async def create_invitation():
    result = await client.out_of_band.create_invitation(
        #auto-accept,
        #create-unique_did,
        multi_use = True,
        body=InvitationCreateRequest(
            accept=["didcomm/aip1", "didcomm/aip2;env=rfc19"],
            #alias,
            #goal,
            goal_code = "did-exchange",
            handshake_protocols=["https://didcomm.org/didexchange/1.1"],
            #mediation_id,
            #meta_data,
            my_label="Cloud Controller Test",
            protocol_version = "1.1",
            #use_did,
            #use_did_method,
            use_public_did = True
        )
    )

    print(result)

async def receive_invitation():
    # parametre se dobi iz invitation_url, ki se ustvari pri create_invitation. Preveri, če se da s kakšnim APIjem dobit ta url, oziroma če se da dobit te podatke iz invitation oziroma connection!

    result = await client.out_of_band.receive_invitation(
        #alias,
        #auto-accept,
        #mediation_id,
        #use_existing_connection
        body=InvitationMessage(
            #id,
            type = "https://didcomm.org/out-of-band/1.1/invitation",
            accept = ["didcomm/aip1", "didcomm/aip2;env=rfc19"],
            #goal,
            #goal_code,
            handshake_protocols = ["https://didcomm.org/didexchange/1.1"],            
            #imageUrl,
            #label,
            #requestsattach,
            services = ["did:sov:4jRbTnf1uzyN5duCZgtiot"]
        )
    )

    print(result)

async def remove_invitation_record():
    result = await client.out_of_band.remove_invitation_record(
        invi_msg_id = "",
    )


## CONNECTION
async def get_connections():
    result = await client.connection.get_connections(
        #alias,
        #connection_protocol,
        #invitation_key,
        #invitation_msg_id,
        #limit,
        #my_did,
        #offset,
        #state,
        #their_did,
        #their_public_did,
        #their_role
    )

    print(result)

async def get_connection():
    result = await client.connection.get_connection(
        conn_id = ""
    )

    print(result)

async def delete_connection():
    result = await client.connection.delete_connection(
        conn_id = ""
    )    

"""
async def run():
    result: InvitationResult = await client.connection.create_invitation(
        body=CreateInvitationRequest(my_label="Cloud Controller")
    )

    # Pydantic v2 introduced strict model typing, so the InvitationResult must be converted to
    # a ReceiveInvitationRequest. These models share identical fields, and so can be converted:
    receive_invitation_request = ReceiveInvitationRequest.from_dict(
        result.invitation.to_dict()
    )

    connection: ConnRecord = await client.connection.receive_invitation(
        body=receive_invitation_request
    )

    print(connection)
"""
## WALLET
async def get_dids():
    DIDsResult = await client.wallet.get_dids()

    print(DIDsResult)

async def create_did():
    result = await client.wallet.create_did(
        body = DIDCreate(method="sov")
    )

    print(result)

async def get_public_did():
    result = await client.wallet.get_public_did()

    print(result)
    return result.did

async def assign_public_did():
    result = await client.wallet.set_public_did(
        did = "VNfo8KDPBWmJQtdwWEvg1A"
    )

    print(result)

async def get_endpoint():
    result = await client.wallet.get_did_endpoint(
        did = "VNfo8KDPBWmJQtdwWEvg1A"
    )

    print(result)
    

## DID EXCHANGE

async def accept_invitation(public_did, connection_id):
    result = await client.did_exchange.accept_invitation(
        conn_id = connection_id,
        #my_endpoint,
        #my_label,
        use_did = public_did,
        #use_did_method
    )

    print(result)

async def accept_request():
    result = await client.did_exchange.accept_request(
        conn_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        #mediation_id,
        #my_endpoint,
        use_public_did = True
    )

    print(result)

async def create_request():
    result = await client.did_exchange.create_request(
        their_public_did = "VNfo8KDPBWmJQtdwWEvg1A",
        #alias,
        #auto_accept,
        #goal,
        #goal_code,
        #mediation_id,
        #my_endpoint,
        my_label = "Test Connection",
        protocol = "didexchange/1.1",
        #use_did,
        #use_did_method
        use_public_did = True
    )

    print(result)


async def reject_exchange():
    result = await client.did_exchange.reject(
        conn_id="3fa85f64-5717-4562-b3fc-2c963f66afa6",
        body=DIDXRejectRequest(reason="Unknown")
    )

    print(result)
    
## ISSUE VC

## PRESENT VC

if __name__ == "__main__":
    # Start webhook server
    webhookserver = start_webhook()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

#asyncio.get_event_loop().run_until_complete(get_connections())
