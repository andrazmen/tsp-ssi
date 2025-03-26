from aries_cloudcontroller import PingRequest

# Send a trust ping to a connection
async def send_ping(client, connection_id, comment):
    result = await client.trustping.send_ping(
        conn_id = connection_id,
        body = PingRequest(
            comment = comment
        )
    )

    return result