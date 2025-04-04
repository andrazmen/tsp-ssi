async def get_connections(client, state, their_did):
    result = await client.connection.get_connections(
        #alias=alias,
        #connection_protocol=connection_protocol,
        #invitation_key=invitation_key,
        #invitation_msg_id=invitation_msg_id,
        #limit=limit,
        #my_did=my_did,
        #offset=offset,
        state=state,
        their_did=their_did,
        #their_public_did=their_public_did,
        #their_role=their_role
    )

    return result

async def get_connection(client, conn_id):
    result = await client.connection.get_connection(
        conn_id = conn_id
    )

    return result

async def delete_connection(client, conn_id):
    result = await client.connection.delete_connection(
        conn_id = conn_id
    )

    return result