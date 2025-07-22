import os
import json
from services.basic_message import send_message
from services.connections import set_metadata

from authentication.cert_authentication import (extract_cn, verify_signature, reconstruct_pem, validate_certificate_chain)

async def create_challenge(event_data):
    try:
        print("Creating challenge...\n")  
        challenge = os.urandom(32)
        print("This is challenge", challenge)
        message = {
            "nonce_value": challenge.hex(),
            "message_type": "offer_request:nonce",
        }
        return message, challenge
    except Exception as e:
        print(f"Error creating challenge: {e}")

async def verify_cert(data):
    certificate = reconstruct_pem(data["certificate"])
    cn = extract_cn(certificate)
    print(f"Received offer request for certificate CN: {cn}")
    valid_chain = validate_certificate_chain(certificate)
    if not valid_chain:
        print(f"Certificate chain for {cn} is not valid")
        return False
    print(f"Certificate chain for {cn} is valid and certificates are within valid period!", "\n")
    return True

async def verify_sign(data, challenge, certificate):
    try:
        print("This is signed challenge:", challenge)
        signature = bytes.fromhex(data["signature_value"])
        cert = reconstruct_pem(certificate)
        verification, cn = verify_signature(cert, challenge, signature)
        if verification == True:
            print(f"Signature is valid for certificate {cn}!","\n")
            return True
        else:
            print("Signature invalid!\n")
            return False
    except Exception as e:
        print(f"Error verifying signature: {e}")