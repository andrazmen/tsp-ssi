async def accept_invitation(client, public_did, connection_id):
    print(public_did)
    print(public_did["did"])
    result = await client.did_exchange.accept_invitation(
        conn_id = connection_id,
        use_did = public_did["did"]
    )
    print(result)

    return result

async def accept_request(client, connection_id):
    result = await client.did_exchange.accept_request(
        conn_id = connection_id,
        use_public_did = True
    )
    print(result)
    return result

async def reject(client, connection_id, description):
    result = await client.did_exchange.reject(
        conn_id = connection_id,
        reason = description
    )
    print(result)
    return result