from indy_vdr import pool, ledger, bindings
from indy_vdr.resolver import Resolver
from anoncreds import Presentation, PresentationRequest, RevocationStatusList

import asyncio
import time
import json
import re

async def connect_to_von_network():
    # Create a pool handle to connect to the von-network ledger
    pool_handle = await pool.open_pool("genesis.txt")
    
    return pool_handle

async def get_schema(pool, did, schema_id):
    schema = {}
    schemas = {}
    schema_req = ledger.build_get_schema_request(did, schema_id)

    response = await pool.submit_request(schema_req)

    schema["name"] = response["data"]["name"]
    schema["issuerId"] = response["dest"]
    schema["version"] = response["data"]["version"]
    schema["attrNames"] = response["data"]["attr_names"]
    schemas[schema_id] = schema

    return schemas

async def get_cred_def(pool, did, cred_def_id, schema_id):
    cred_def = {}
    cred_defs = {}
    cred_def_req = ledger.build_get_cred_def_request(did, cred_def_id)

    response = await pool.submit_request(cred_def_req)

    cred_def["issuerId"] = response["origin"]
    cred_def["schemaId"] = schema_id
    cred_def["type"] = response["signature_type"]
    cred_def["tag"] = response["tag"]
    cred_def["value"] = response["data"]

    cred_defs[cred_def_id] = cred_def

    return cred_defs

async def get_rev_reg_def(pool, did, rev_reg_id):
    rev_reg = {}
    rev_regs = {}
    rev_reg_def_req = ledger.build_get_revoc_reg_def_request(did, rev_reg_id)

    response = await pool.submit_request(rev_reg_def_req)

    match = re.match(r'([A-Za-z0-9]+):', response["data"]["id"])
    rev_reg["issuerId"] = match.group(1)
    rev_reg["revocDefType"] = response["data"]["revocDefType"]
    rev_reg["credDefId"] = response["data"]["credDefId"]
    rev_reg["tag"] = response["data"]["tag"]
    rev_reg["value"] = response["data"]["value"]

    rev_regs[rev_reg_id] = rev_reg

    return rev_regs

async def get_rev_list(pool, did, rev_reg, timestamp):
    rev_list = {}
    #rev_lists = {}
    rev_list_req = ledger.build_get_revoc_reg_delta_request(did, rev_reg, 0, timestamp)

    response = await pool.submit_request(rev_list_req)

    #print(response)

    match = re.match(r'([A-Za-z0-9]+):', response["revocRegDefId"])
    rev_list["issuerId"] = match.group(1)
    rev_list["revRegDefId"] = response["revocRegDefId"]
    rev_list["revocationList"] = response["data"]["value"]["revoked"]
    rev_list["currentAccumulator"] = response["data"]["value"]["accum_to"]["value"]["accum"]
    rev_list["timestamp"] = response["to"]

    rev_lists = [rev_list]

    return rev_lists

async def verify_pres(pres, req, schemas, cred_defs, rev_reg_defs, rev_lists):

    #rev_list = rev_lists
    
    verified = pres.verify(req, schemas, cred_defs, rev_reg_defs, rev_lists)

    print(verified)

async def main():
    timestamp = int(time.time())

    with open("pres.json") as f:
        pres_json = json.load(f)

    pres_json["identifiers"][0]["timestamp"] = timestamp
    mod_pres = json.dumps(pres_json)
    pres = Presentation.load(pres_json)
    print("Presentation:", pres.to_json(), "\n")

    with open("req.json") as f:
        req_json = json.load(f)

    req = PresentationRequest.load(req_json)
    print("Presentation request:", req.to_json(), "\n")

    did = "AhNYx5Cp2rK3mXmUtNiQtd"
    schema_id = "VWJgMNS75SWMpkp2gT74Zq:2:AuthCredential:1.0.0"
    cred_def_id = "VWJgMNS75SWMpkp2gT74Zq:3:CL:13:default"
    rev_reg_id = "VWJgMNS75SWMpkp2gT74Zq:4:VWJgMNS75SWMpkp2gT74Zq:3:CL:13:default:CL_ACCUM:0"
    #timestamp = pres_json["identifiers"][0]["timestamp"]

    pool_handle = await connect_to_von_network()

    schemas = await get_schema(pool_handle, did, schema_id)
    print("Schemas:", schemas, "\n")

    cred_defs = await get_cred_def(pool_handle, did, cred_def_id, schema_id)
    print("Credential definitions:", cred_defs, "\n")

    rev_reg_defs = await get_rev_reg_def(pool_handle, did, rev_reg_id)
    print("Revocation registry definitions:", rev_reg_defs, "\n")

    rev_lists = await get_rev_list(pool_handle, did, rev_reg_id, timestamp)
    print("Revocation lists:", rev_lists, "\n")


    verified = await verify_pres(pres, req, schemas, cred_defs, rev_reg_defs, rev_lists)

# Run the main function asynchronously
asyncio.run(main())