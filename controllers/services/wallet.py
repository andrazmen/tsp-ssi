from aries_cloudcontroller import DIDCreate

async def get_dids(client):
    result = await client.wallet.get_dids()
    dids_dict = result.to_dict()
    dids = dids_dict["results"]

    return dids

async def create_did(client, type):
    result = await client.wallet.create_did(
        body = DIDCreate(method=type)
    )
    did_dict = result.to_dict()
    did = did_dict["result"]

    return did

async def get_public_did(client):
    result = await client.wallet.get_public_did()

    did_dict = result.to_dict()
    did = did_dict["result"]

    return did

async def assign_public_did(client, did):
    res = await client.wallet.set_public_did(
        did=did
    )
    did_dict = res.to_dict()
    result = did_dict["result"]

    return result