from aries_cloudcontroller import DIDCreate, DIDEndpointWithType

## DIDS
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

async def get_did_endpoint(client, did):
    result = await client.wallet.get_did_endpoint(
        did=did
    )
    return result

async def set_did_endpoint(client, did, url):
    result = await client.wallet.set_did_endpoint(
        body = DIDEndpointWithType(
            did=did,
            endpoint=url
        )
    )
    return result

## CREDENTIALS
async def delete_credential(client, cred_id):
    result = await client.credentials.delete_record(
        credential_id = cred_id
    )
    return result

async def get_credential(client, cred_id):
    result = await client.credentials.get_record(
        credential_id = cred_id
    )
    return result

async def get_credentials(client):
    result = await client.credentials.get_records()
    vcs_dict = result.to_dict()
    vcs = vcs_dict["results"]
    return vcs

async def get_revocation_status(client, cred_id):
    result = await client.credentials.get_revocation_status(
        credential_id = cred_id
    )
    return result

async def rotate_keypair(client, did):
    result = await client.wallet.rotate_keypair(
        did=did
    )
    return result