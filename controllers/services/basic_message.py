from aries_cloudcontroller import SendMessage

async def send_message(client, conn_id, message):
    result = await client.basicmessage.send_message(
        conn_id = conn_id,
        body = SendMessage(content = message)
    )
    return(result)