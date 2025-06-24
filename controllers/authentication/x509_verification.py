import os
import json
from services.basic_message import send_message
from services.connections import set_metadata

from authentication.cert_authentication import (verify_signature, reconstruct_pem, validate_certificate_chain)

async def create_challenge(client, conn_id, vp, data):
    try:
        if vp:
            conn_id = vp["connection_id"] 
            attrs = vp["by_format"]["pres"]["anoncreds"]["requested_proof"]["revealed_attr_groups"]["auth_attr"]["values"]
            print("Creating challenge...\n")  
            #global challenge  
            challenge = os.urandom(32)
            if attrs.get("credential_type").get("raw") == "authorization":
                message = {
                    "type": "nonce",
                    "value": challenge.hex(),
                    "cred_type": attrs.get("credential_type").get("raw"),
                    "id": attrs.get("authorizee_cn").get("raw")
                }
            elif attrs.get("credential_type").get("raw") == "technical":
                message = {
                    "type": "nonce",
                    "value": challenge.hex(),
                    "cred_type": attrs.get("credential_type").get("raw"),
                    "id": attrs.get("subject_cn").get("raw")
                }
            print(f"Sending challenge to connection with ID: {conn_id}...","\n")
            await send_message(client, conn_id, json.dumps(message))
        elif data:
            print("Creating challenge...\n")  
            #global challenge  
            challenge = os.urandom(32)
            print("This is challenge", challenge)
            message = {
                "type": "nonce",
                "value": challenge.hex(),
                "cred_type": data["cred_type"],
                "id": data["id"]
            }
            print(f"Sending challenge to connection with ID: {conn_id}...","\n")
            await send_message(client, conn_id, json.dumps(message))
        return challenge
    except Exception as e:
        print(f"Error creating challenge: {e}")

async def verify_cert(data):
    certificate = reconstruct_pem(data["certificate"])
    #valid = check_expiration(certificate)
    #if not valid:
    #    print(f"Certificate expiration is not valid")
    #    return False

    valid_chain = validate_certificate_chain(certificate)
    if not valid_chain:
        print(f"Certificate chain {data["id"]} is not valid")
        return False
    print(f"Certificate chain for {data["id"]} is valid and certificates are within valid period!", "\n")
    return True

async def verify_sign(client, conn_id, data, challenge):
    try:
        #print("Verifying signature...\n")
        print("This is challenge in vs:", challenge)
        signature = bytes.fromhex(data["value"])
        certificate = reconstruct_pem(data["certificate"])
        verification, cn = verify_signature(certificate, challenge, signature)
        if cn == data["id"]:
            if verification == True:
                print(f"Signature is valid for certificate {cn}!","\n")
                #await set_metadata(client, conn_id, cn)
                return True
            else:
                print("Signature invalid!\n")
                return False
        else:
            print("Certificate CN does not match with the one in the proof!\n")
            return False
    except Exception as e:
        print(f"Error verifying signature: {e}")