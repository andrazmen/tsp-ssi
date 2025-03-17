from aries_cloudcontroller import (InvitationCreateRequest, InvitationMessage)

async def create_invitation(client):
    result = await client.out_of_band.create_invitation(
        #auto-accept,
        #create-unique_did,
        multi_use = True,
        body=InvitationCreateRequest(
            accept = ["didcomm/aip1", "didcomm/aip2;env=rfc19"],
            alias = "test1",
            goal = "DID exchange", 
            goal_code = "did-exchange",
            handshake_protocols = ["https://didcomm.org/didexchange/1.1"],
            #mediation_id,
            #meta_data,
            my_label = "Invitation for DID exchange",
            protocol_version = "1.1",
            #use_did,
            #use_did_method,
            use_public_did = True
        )
    )

    return result

async def receive_invitation(client, invitation_msg):
    inv_msg = InvitationMessage.from_dict(invitation_msg)
    result = await client.out_of_band.receive_invitation(
        #alias,
        #auto-accept,
        #mediation_id,
        #use_existing_connection
        body=inv_msg
    )

    print(result)