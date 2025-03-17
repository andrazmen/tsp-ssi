async def accept_invitation(client, public_did, connection_id):
    result = await client.did_exchange.accept_invitation(
        conn_id = connection_id,
        use_did = public_did.result.did
    )
    print(result)

async def accept_request(client, connection_id):
    result = await client.did_exchange.accept_request(
        conn_id = connection_id,
        #mediation_id,
        #my_endpoint,
        use_public_did = True
    )

    print(result)