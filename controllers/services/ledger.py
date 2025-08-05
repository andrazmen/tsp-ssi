async def register_nym(client, did, verkey):
    result = await client.ledger.register_nym(
        did = did,
        verkey = verkey
    )
    return result