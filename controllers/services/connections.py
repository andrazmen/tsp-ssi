from aries_cloudcontroller import (ConnectionMetadataSetRequest)

async def get_connections(client, state, their_did):
    result = await client.connection.get_connections(
        state=state,
        their_did=their_did
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

async def get_metadata(client, conn_id):
    result = await client.connection.get_metadata(
        conn_id = conn_id
    )

    return result

async def set_metadata(client, conn_id, certificate_cn):
    result = await client.connection.set_metadata(
        conn_id = conn_id,
        body = ConnectionMetadataSetRequest(
            metadata = {
                certificate_cn: True
            }
        )
    )

    return result