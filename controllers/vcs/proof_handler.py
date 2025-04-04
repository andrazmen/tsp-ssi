import time
import json

from aiocache import cached

from .check_revocation import get_rev_list

@cached(ttl=60)
async def get_proof(submitter_did, did, records):
    result = {}
    for r in records:
        pres_ex_id = r["pres_ex_id"]
        cred_rev_id = r["by_format"]["pres"]["anoncreds"]["requested_proof"]["self_attested_attrs"]["cred_rev_id"]
        rev_reg_id = r["by_format"]["pres"]["anoncreds"]["identifiers"][0]["rev_reg_id"]
        try:
            print("Checking credential revocation status...")
            response = await get_rev_list(submitter_did, rev_reg_id, cred_rev_id)
            if response == True:
                print("Credential in proof is revoked...", "\n")
            elif response == False:
                print("Credential in proof is stil valid!", "\n")
                result[pres_ex_id] = {"did": did, "connection_id": r["connection_id"], "data": r["by_format"]["pres"]["anoncreds"]["requested_proof"], "identifiers": r["by_format"]["pres"]["anoncreds"]["identifiers"]}
        except Exception as e:
            print(f"Error checking credentials revocation status: {e}")  
    
    return result

