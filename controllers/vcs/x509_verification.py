import os
import json
from services.basic_message import send_message
from services.connections import set_metadata

from authentication.cert_authentication import (verify_signature, reconstruct_pem)

async def create_challenge(client, vp):
    try:
        conn_id = vp["connection_id"] 
        attrs = vp["by_format"]["pres"]["anoncreds"]["requested_proof"]["revealed_attr_groups"]["auth_attr"]["values"]
        print("Creating challenge...\n")  
        global challenge  
        challenge = os.urandom(32)
        if attrs.get("credential_type").get("raw") == "authorization":
            message = {
                "type": "nonce",
                "value": challenge.hex(),
                "cred_type": attrs.get("credential_type").get("raw"),
                "id": attrs.get("authorizee_cn").get("raw")
            }
        elif attrs.get("credential_type").get("raw") == "technical":
            # todo: verify TA
            message = {
                "type": "nonce",
                "value": challenge.hex(),
                "cred_type": attrs.get("credential_type").get("raw"),
                "id": attrs.get("subject_cn").get("raw")
            }
        print(f"Sending challenge to connection with ID: {conn_id}...","\n")
        await send_message(client, conn_id, json.dumps(message))

    except Exception as e:
        print(f"Error creating challenge: {e}")

async def verify_sign(client, conn_id, data):
    try:
        #print("Verifying signature...\n")
        signature = bytes.fromhex(data["value"])
        certificate = reconstruct_pem(data["certificate"])
        verification, cn = verify_signature(certificate, challenge, signature)
        if cn == data["id"]:
            if verification == True:
                print(f"Signature is valid for certificate {cn}!","\n")
                await set_metadata(client, conn_id, cn)
                return True
            else:
                print("Signature invalid!\n")
                return False
        else:
            print("Certificate CN does not match with the one in the proof!\n")
            return False
    except Exception as e:
        print(f"Error verifying signature: {e}")