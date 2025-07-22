import time
from datetime import datetime
import json
import hashlib

from aiocache import caches, Cache, cached

from .check_revocation import get_rev_list
from services.connections import get_metadata, get_connection
from services.present_proof import delete_pres_record, get_pres_records
from services.basic_message import send_message
"""
cache=Cache.MEMORY

def generate_key(arg1, arg2):
    key_input = f"{arg1}:{arg2}".encode("utf-8")
    hash_digest = hashlib.sha256(key_input).hexdigest()
    return f"get_proofs:{hash_digest}"

def custom_key_builder(func, *args):
    # Extract the first two positional args (arg1, arg2)
    arg1 = args[3]
    arg2 = args[5]
    print("args:", arg1, arg2)
    
    #print(f"Building key {func.__name__}:{hash_digest}")
    #return f"{func.__name__}:{hash_digest}"
    #return f"{func.__name__}:{arg1}:{arg2}"
    key = generate_key(arg1, arg2)
    print(F"Bulding key {key}")
    return key

async def invalidate_cache(arg1, arg2):
    #key_input = f"{arg1}:{arg2}".encode("utf-8")
    #hash_digest = hashlib.sha256(key_input).hexdigest()
    #key = f"get_proofs:{hash_digest}"
    key = generate_key(arg1, arg2)
    
    print(f"Ready to delete key {key}")
    #print(f"Ready to delete key get_proofs:{hash_digest}")
    #key = f"get_proofs:{arg1}:{arg2}"
    print("Before delete:", await caches.get("default").exists(key))
    #await caches.get("default").delete(key)
    await caches.get("default").clear()
"""
#@cached(ttl=600, cache=cache, key_builder=custom_key_builder)
@cached(ttl=600)
async def get_proofs(client, event_data, records, requester_cn, submitter_did, topic):
    result_item = {}
    result = {} 
    try:
        if event_data:
            pres_ex_id = event_data["pres_ex_id"]
            values = event_data["by_format"]["pres"]["anoncreds"]["requested_proof"]["revealed_attr_groups"]["auth_attr"]["values"]
            subject = values.get("subject_cn", {})
            if values.get("credential_type", {}).get("raw") == "technical":
                print("Credential type is TechCredential!")
                identifiers = event_data["by_format"]["pres"]["anoncreds"]["identifiers"][0]
                identifiers["cred_rev_id"] = event_data["by_format"]["pres"]["anoncreds"]["requested_proof"]["self_attested_attrs"]["cred_rev_id"]
                result[pres_ex_id] = {"issuer_cn": values.get("issuer_cn", {}).get("raw"), "issuer_did": values.get("issuer_did", {}).get("raw"), "subject_cn": values.get("subject_cn").get("raw"), "subject_did": values.get("subject_did").get("raw"), "data": {k: v.get("raw") for k, v in values.items()}, "identifiers": identifiers}   
                print("Technical credential valid, chain cached")
                return result

            elif values.get("credential_type", {}).get("raw") == "authorization":
                print("Credential type is not TechCredential, checking chained proofs...")
                identifiers = event_data["by_format"]["pres"]["anoncreds"]["identifiers"][0]
                identifiers["cred_rev_id"] = event_data["by_format"]["pres"]["anoncreds"]["requested_proof"]["self_attested_attrs"]["cred_rev_id"]
                result_item[pres_ex_id] = {"issuer_cn": values.get("issuer_cn", {}).get("raw"), "issuer_did": values.get("issuer_did", {}).get("raw"), "subject_cn": values.get("subject_cn").get("raw"), "subject_did": values.get("subject_did").get("raw"), "data": {k: v.get("raw") for k, v in values.items()}, "identifiers": identifiers}
                # Check chain proofs based on leaf auth proof
                proofs = await check_chain(client, result_item, topic)
                if proofs:
                    revoked_proofs = await check_revocation_status(client, submitter_did, proofs)
                    if revoked_proofs == None:
                        print("Error checking revocation status, returning empty result.")
                        return {}
                    if revoked_proofs:
                        print("Revoked proofs found:", revoked_proofs)
                        for proof in revoked_proofs:
                            print(f"Credential in proof {proof} is revoked! Deleting proof...", "\n")
                            await handle_proof_delete(client, event_data)
                            return {}
                    return proofs
                else:
                    print("No chained proofs found, deleting proof...")
                    await handle_proof_delete(client, event_data)
                    return {}
            else:
                print("Credential type is neither AuthCredential nor TechCredential, deleting proof...")
                await handle_proof_delete(client, event_data)
                return {}
        for r in records:
            print("Get proof:", r["pres_ex_id"])
            values = r["by_format"]["pres"]["anoncreds"]["requested_proof"]["revealed_attr_groups"]["auth_attr"]["values"]
            subject = values.get("subject_cn", {})
            # Search for identity match
            if requester_cn == subject.get("raw"):
                pres_ex_id = r["pres_ex_id"]
                # Check credential type
                if values.get("credential_type", {}).get("raw") == "technical":
                    print("Credential type is TechCredential!")
                    # Check cem id
                    resource = values.get("resource", {}).get("raw")
                    cem_id = resource.split("/")[resource.split("/").index("cem_id") + 1]
                    if not topic.split("/")[2] == cem_id:
                        print("Topic does not match, skipping...")
                        continue
                    identifiers = r["by_format"]["pres"]["anoncreds"]["identifiers"][0]
                    identifiers["cred_rev_id"] = r["by_format"]["pres"]["anoncreds"]["requested_proof"]["self_attested_attrs"]["cred_rev_id"]
                    result[pres_ex_id] = {"issuer_cn": values.get("issuer_cn", {}).get("raw"), "issuer_did": values.get("issuer_did", {}).get("raw"), "subject_cn": values.get("subject_cn").get("raw"), "subject_did": values.get("subject_did").get("raw"), "data": {k: v.get("raw") for k, v in values.items()}, "identifiers": identifiers}
                    # Check revocation
                    revoked_proofs = await check_revocation_status(client, submitter_did, result)
                    if revoked_proofs == None:
                        print("Error checking revocation status, returning empty result.")
                        result = {}
                    if r["pres_ex_id"] in revoked_proofs:
                        print(f"Credential in proof {pres_ex_id} is revoked! Deleting proof...", "\n")
                        await handle_proof_delete(client, r)
                        result = {}
                    return result
                elif (values.get("credential_type", {}).get("raw") == "authorization"):
                    # Check topic
                    if not topic == values.get("resource", {}).get("raw"):
                        print("Topic does not match, skipping...")
                        continue
                    print("Credential type is not TechCredential, checking chained proofs...")
                    identifiers = r["by_format"]["pres"]["anoncreds"]["identifiers"][0]
                    identifiers["cred_rev_id"] = r["by_format"]["pres"]["anoncreds"]["requested_proof"]["self_attested_attrs"]["cred_rev_id"]
                    result_item[pres_ex_id] = {"issuer_cn": values.get("issuer_cn", {}).get("raw"), "issuer_did": values.get("issuer_did", {}).get("raw"), "subject_cn": values.get("subject_cn").get("raw"), "subject_did": values.get("subject_did").get("raw"), "data": {k: v.get("raw") for k, v in values.items()}, "identifiers": identifiers}
                    # Check chain proofs based on leaf auth proof
                    proofs = await check_chain(client, result_item, topic)
                    if proofs:
                        revoked_proofs = await check_revocation_status(client, submitter_did, proofs)
                        if revoked_proofs == None:
                            print("Error checking revocation status, returning empty result.")
                            return {}
                        if revoked_proofs:
                            print("Revoked proofs found:", revoked_proofs)
                            for proof in revoked_proofs:
                                print(f"Credential in proof {proof} is revoked! Deleting proof...", "\n")
                                await handle_proof_delete(client, next((rec for rec in records if rec["pres_ex_id"] == proof), None))
                            return {}
                        return proofs
                else:
                    print("Credential type is neither AuthCredential nor TechCredential, skipping...")
                    continue
        return {} 
    except Exception as e:
            print(f"Error getting proofs: {e}")
            return {}  

async def check_chain(client, initial_proof, topic):
    # Fetch updated records
    recs = await get_pres_records(client, connection_id=None, role="verifier", state="done")
    records_dict = recs.to_dict()
    records = records_dict["results"]
    # Copy input
    leaf_proof = initial_proof.copy()
    print("Leaf proof:", leaf_proof)

    # Helpers
    result = {}
    valid_proof = {}
    result.update(leaf_proof)

    # Initial values
    issuer = next(iter(leaf_proof.values())).get("issuer_cn")
    print("Initial issuer:", issuer)

    i = 0
    try:
        while i < len(records):
            # Avoid current and verified auth proof
            if records[i]["pres_ex_id"] == next(iter(leaf_proof)) or records[i]["pres_ex_id"] in result:
                i += 1
                continue
            print("runda:", i)
            r = records[i]
            print("Check chain:", r["pres_ex_id"])
            values = r["by_format"]["pres"]["anoncreds"]["requested_proof"]["revealed_attr_groups"]["auth_attr"]["values"]
            subject = values.get("subject_cn", {})
            # Search for identity match
            if issuer == subject.get("raw"):
                pres_ex_id = r["pres_ex_id"]
                # Check credential type
                if values.get("credential_type", {}).get("raw") == "technical":
                    print("Credential type is TechCredential!")
                    # Check cem id
                    resource = values.get("resource", {}).get("raw")
                    cem_id = resource.split("/")[resource.split("/").index("cem_id") + 1]
                    if not topic.split("/")[2] == cem_id:
                        print("Topic does not match, skipping...")
                        i += 1
                        continue
                    identifiers = r["by_format"]["pres"]["anoncreds"]["identifiers"][0]
                    identifiers["cred_rev_id"] = r["by_format"]["pres"]["anoncreds"]["requested_proof"]["self_attested_attrs"]["cred_rev_id"]
                    result[pres_ex_id] = {"issuer_cn": values.get("issuer_cn", {}).get("raw"), "issuer_did": values.get("issuer_did", {}).get("raw"), "subject_cn": values.get("subject_cn").get("raw"), "subject_did": values.get("subject_did").get("raw"), "data": {k: v.get("raw") for k, v in values.items()}, "identifiers": identifiers}
                    print("Found valid technical credential, chain cached")
                    return result
                elif (values.get("credential_type", {}).get("raw") == "authorization"):
                    print("Credential type is AuthCredential, checking attributes...")
                    valid_proof = {}
                    # Check topic
                    if not topic == values.get("resource", {}).get("raw"):
                        print("Topic does not match, skipping...")
                        i += 1
                        continue
                    # Check action
                    if not bool(set(json.loads(values.get("actions", {}).get("raw"))) & set(json.loads(next(iter(leaf_proof.values())).get("data", {}).get("actions", {})))):
                        print("Action does not match, skipping...")
                        i += 1
                        continue
                    # Check authorization interval
                    if datetime.fromisoformat(values.get("valid_from", {}).get("raw")).timestamp() < datetime.fromisoformat(next(iter(leaf_proof.values())).get("data").get("valid_from", {})).timestamp() or datetime.fromisoformat(values.get("valid_until", {}).get("raw")).timestamp() > datetime.fromisoformat(next(iter(leaf_proof.values())).get("data").get("valid_until", {})).timestamp():
                        print("Authorization interval does not match, skipping...")
                        i += 1
                        continue
                    # Check time slot
                    if not bool(set(json.loads(values.get("time_slot", {}).get("raw"))) & set(json.loads(next(iter(leaf_proof.values())).get("data").get("time_slot", {})))):
                        print("Time slot does not match, skipping...")
                        i += 1
                        continue 
                    identifiers = r["by_format"]["pres"]["anoncreds"]["identifiers"][0]
                    identifiers["cred_rev_id"] = r["by_format"]["pres"]["anoncreds"]["requested_proof"]["self_attested_attrs"]["cred_rev_id"]                       
                    valid_proof[pres_ex_id] = {"issuer_cn": values.get("issuer_cn", {}).get("raw"), "issuer_did": values.get("issuer_did", {}).get("raw"), "subject_cn": values.get("subject_cn").get("raw"), "subject_did": values.get("subject_did").get("raw"), "data": {k: v.get("raw") for k, v in values.items()}, "identifiers": identifiers}
                    result.update(valid_proof)
                    issuer = values.get("issuer_cn", {}).get("raw")
                    leaf_proof = valid_proof
                    print("new leaf proof", leaf_proof)
                    i = 0
                else:
                    print("Credential type is neither AuthCredential nor TechCredential, skipping...")
                    i += 1
            else:
                i += 1 
        return {}
    except Exception as e:
        print(f"Error checking chained proofs: {e}")
        return {}

async def check_revocation_status(client, submitter_did, vps):
    rev_lists = {}
    revoked_proofs = []
    try:
        for r in vps:
            cred_rev_id = vps[r].get("identifiers", {}).get("cred_rev_id")
            rev_reg_id = vps[r].get("identifiers", {}).get("rev_reg_id")
            if rev_reg_id not in rev_lists:
                rev_list = await ledger_handler(submitter_did, rev_reg_id, rev_lists)
                rev_lists.update(rev_list)
            if int(cred_rev_id) in rev_lists[rev_reg_id]:
                print(f"Credential with cred_rev_id {cred_rev_id} is revoked!", "\n")
                revoked_proofs.append(r)
                print("Revoked proofs:", revoked_proofs)
        return revoked_proofs
    except Exception as e:
        print(f"Error checking revocation status: {e}")
        return None

# Fetch revocation list from ledger
async def ledger_handler(submitter_did, rev_reg_id, rev_lists):
    print("Fetching revocation list from ledger...")
    response = await get_rev_list(submitter_did, rev_reg_id)

    rev_lists[rev_reg_id] = response
    print("Revocation list attached to revocations lists:", rev_lists, "\n")
    
    return rev_lists

async def handle_proof_delete(client, event_data):
    try:
        print(f"Deleting presentation exchange record {event_data['pres_ex_id']}...\n")
        result = await delete_pres_record(client, event_data["pres_ex_id"])
        print(f"Presentation exchange record deleted: {result}")
        await send_message(client, event_data["connection_id"], f"Presentation exchange record {event_data['pres_ex_id']} deleted due to verification failure.")
    except Exception as e:
        print(f"Error deleting presentation exchange record: {e}")
