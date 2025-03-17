async def get_connections(
    client,
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

    return result