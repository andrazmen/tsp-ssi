import json

from aries_cloudcontroller import (InvitationCreateRequest, InvitationMessage)

from utils.tools import (extract_oob, decode)

async def create_invitation(client, invitation):
    result = await client.out_of_band.create_invitation(
        #auto_accept = True,
        #create-unique_did,
        #multi_use = True,
        body = InvitationCreateRequest.from_json(invitation)
    )

    return result

async def receive_invitation(client, url):
    encoded_invitation = extract_oob(url)
    print("t:", type(encoded_invitation))
    decoded_invitation = decode(encoded_invitation)
    invitation_msg = json.loads(decoded_invitation) 
    inv_msg = InvitationMessage.from_dict(invitation_msg)
    result = await client.out_of_band.receive_invitation(
        #alias,
        #auto_accept = True,
        #mediation_id,
        #use_existing_connection = True,
        body=inv_msg
    )

    print(result)

async def delete_invitation(client, invi_msg_id):
    result = await client.out_of_band.remove_invitation_record(
        invi_msg_id = invi_msg_id
    )

    print(result)