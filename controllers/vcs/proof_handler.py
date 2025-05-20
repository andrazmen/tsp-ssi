import time
import json

from aiocache import cached

from .check_revocation import get_rev_list
from services.connections import get_metadata

rev_lists = {}
dead_proofs = []
loop_proofs = []
revoked_proofs = []
topic_mismatch_proofs = []

#@cached(ttl=60)
async def get_proofs(client, records, requester_cn, submitter_did, topics):
    result = {} 
    try:
        for r in records:
            print("Get proof:", r["pres_ex_id"])
            values = r["by_format"]["pres"]["anoncreds"]["requested_proof"]["revealed_attr_groups"]["auth_attr"]["values"]
            subject = values.get("subject_cn")
            authorizee = values.get("authorizee_cn")
            # Search for identity match
            if (subject and requester_cn == subject.get("raw")) or (authorizee and requester_cn == authorizee.get("raw")):
                pres_ex_id = r["pres_ex_id"]
                cred_rev_id = r["by_format"]["pres"]["anoncreds"]["requested_proof"]["self_attested_attrs"]["cred_rev_id"]
                rev_reg_id = r["by_format"]["pres"]["anoncreds"]["identifiers"][0]["rev_reg_id"]
                # Check revocation
                if rev_reg_id not in rev_lists:
                    rev_lists.update(await ledger_handler(submitter_did, rev_reg_id, rev_lists))
                #if cred_rev_id in rev_lists[rev_reg_id]:
                if cred_rev_id in []:
                    print(f"Credential with cred_rev_id {cred_rev_id} is revoked!", "\n")
                    revoked_proofs.append(r["pres_ex_id"])
                    print("Revoked proofs:", revoked_proofs)

                    dead_proofs.append(r["pres_ex_id"])
                    continue
                else:
                    print(f"Credential in proof {r["pres_ex_id"]} is valid!", "\n")
                    pres_ex_id = r["pres_ex_id"]

                    result_item = {}
                    # Check credential type
                    if values.get("credential_type").get("raw") == "technical":
                        print("Credential type is TechCredential!")
                        # Check certificate CN
                        metadata = await get_metadata(client, r["connection_id"])
                        if subject not in metadata.get(results):
                            print("Unknown certificate CN, skipping...")
                            continue
                        result_item[pres_ex_id] = {"issuer_cn": values.get("issuer_cn").get("raw"), "issuer_did": values.get("issuer_did").get("raw"), "subject_cn": values.get("subject_cn").get("raw"), "subject_did": values.get("subject_did").get("raw"), "data": {k: v.get("raw") for k, v in values.items()}}
                        result[len(result) + 1] = result_item
                    elif (values.get("credential_type").get("raw") == "authorization"):
                        # Check certificate CN
                        metadata = await get_metadata(client, r["connection_id"])
                        if authorizee not in metadata.get(results):
                            print("Unknown certificate CN, skipping...")
                            continue
                        # Check topic
                        print("My topic:", topics)
                        print("Topics in proof:", values.get("topics").get("raw"))
                        if topics in json.loads(values.get("topics").get("raw")):
                            print("Credential type is not TechCredential, checking chained proofs...")
                            result_item[pres_ex_id] = {"authorizer_cn": values.get("authorizer_cn").get("raw"), "authorizer_did": values.get("authorizer_did").get("raw"), "authorizee_cn": values.get("authorizee_cn").get("raw"), "authorizee_did": values.get("authorizee_did").get("raw"), "data": {k: v.get("raw") for k, v in values.items()}}
                            # Check chain proofs based on root auth proof
                            proofs = await check_chain(records, result_item, submitter_did, topics)
                            if proofs:
                                result[len(result) + 1] = proofs
                        else:
                            print("Topics does not match, skipping...")
                            topic_mismatch_proofs.append(r["pres_ex_id"])
                            dead_proofs.append(r["pres_ex_id"])
        return result
    except Exception as e:
            print(f"Error getting proofs: {e}")
            return {}  

async def check_chain(records, initial_proof, submitter_did, topics):
    # Copy input
    chained_proofs = initial_proof.copy()

    # Helpers
    prev_proofs = {}
    holders = []
    verified_proofs = []
    result = {}

    # Initial values
    issuer = next(iter(chained_proofs.values())).get("authorizer_cn")
    holder = next(iter(chained_proofs.values())).get("authorizee_cn")
    holders.append(holder)
    print("Initial issuer:", issuer)
    print("Initial holder:", holder)
    
    i = 0
    try:
        while i < len(records):
            print("Dead proofs:", dead_proofs)
            print("Verified proofs:", verified_proofs)
            # Avoid root auth proof, dead proofs and verified proofs
            if records[i]["pres_ex_id"] != next(iter(initial_proof.values())).get("pres_ex_id") and records[i]["pres_ex_id"] not in dead_proofs and records[i]["pres_ex_id"] not in verified_proofs:
                print("runda:", i)
                r = records[i]
                print("Check chain:", r["pres_ex_id"])
                values = r["by_format"]["pres"]["anoncreds"]["requested_proof"]["revealed_attr_groups"]["auth_attr"]["values"]
                subject = values.get("subject_cn")
                authorizee = values.get("authorizee_cn")
                # Search for identity match
                if (subject and issuer == subject.get("raw")) or (authorizee and issuer == authorizee.get("raw")):
                    print("Prev_proof before loop check:", prev_proofs.keys()) 
                    if authorizee: print(i, (authorizee.get("raw")), holders)
                    # Check for loop
                    if (authorizee and (authorizee.get("raw") in holders) or (subject and (subject.get("raw") in holders))):
                        print("Loop detected, skipping...")
                        if prev_proofs != {}:
                            loop_proofs.extend(list(prev_proofs.keys()))
                            print("Loop proofs:", loop_proofs)
                            dead_proofs.extend(loop_proofs)
                        # RESET
                        chained_proofs, prev_proofs, issuer, holder, holders = reset_chain(initial_proof, holders)
                        i = 0
                        continue

                    # Check revocation
                    cred_rev_id = r["by_format"]["pres"]["anoncreds"]["requested_proof"]["self_attested_attrs"]["cred_rev_id"]
                    rev_reg_id = r["by_format"]["pres"]["anoncreds"]["identifiers"][0]["rev_reg_id"]
                    if rev_reg_id not in rev_lists:
                        rev_lists.update(await ledger_handler(submitter_did, rev_reg_id, rev_lists))
    
                    #if cred_rev_id in rev_lists[rev_reg_id]:
                    if cred_rev_id in []:
                        print(f"Credential with cred_rev_id {cred_rev_id} is revoked!", "\n")

                        revoked_proofs.append(r["pres_ex_id"])
                        print("Revoked proofs:", revoked_proofs)

                        dead_proofs.extend(list(prev_proofs.keys()))
                        dead_proofs.append(r["pres_ex_id"])

                        # RESET
                        chained_proofs, prev_proofs, issuer, holder, holders = reset_chain(initial_proof, holders)
                        i = 0
                        continue
                    else:
                        print(f"Credential in proof {r["pres_ex_id"]} is valid!", "\n")
                        pres_ex_id = r["pres_ex_id"]

                        # Check credential type
                        if values.get("credential_type").get("raw") == "technical":
                            print("Credential type is TechCredential!")
                            chained_proofs.update(prev_proofs)
                            chained_proofs[pres_ex_id] = {"issuer_cn": values.get("issuer_cn").get("raw"), "issuer_did": values.get("issuer_did").get("raw"), "subject_cn": values.get("subject_cn").get("raw"), "subject_did": values.get("subject_did").get("raw"), "data": {k: v.get("raw") for k, v in values.items()}}

                            verified_proofs.extend(list(chained_proofs.keys()))
                            print("Verified proofs:", verified_proofs)
                            result[len(result) + 1] = chained_proofs
                            # Check for other chains (RESET)
                            chained_proofs, prev_proofs, issuer, holder, holders = reset_chain(initial_proof, holders)
                            i = 0
                            continue
                            
                        elif (values.get("credential_type").get("raw") == "authorization"):
                            if topics in json.loads(values.get("topics").get("raw")):
                                print("Credential type is not TechCredential, checking proofs...")
                                prev_proofs[pres_ex_id] = {"authorizer_cn": values.get("authorizer_cn").get("raw"), "authorizer_did": values.get("authorizer_did").get("raw"), "authorizee_cn": values.get("authorizee_cn").get("raw"), "authorizee_did": values.get("authorizee_did").get("raw"), "data": {k: v.get("raw") for k, v in values.items()}}
                                issuer = values.get("authorizer_cn").get("raw")
                                holder = values.get("authorizee_cn").get("raw")
                                holders.append(holder)
                                print("Updated holders:", holders)
                                i = 0
                            else:
                                print("Topics does not match, skipping...")
                                topic_mismatch_proofs.append(r["pres_ex_id"])
                                dead_proofs.extend(list(prev_proofs.keys()))
                                dead_proofs.append(r["pres_ex_id"])
                                # RESET
                                chained_proofs, prev_proofs, issuer, holder, holders = reset_chain(initial_proof, holders)
                                i = 0
                        else:
                            print("Credential type is neither AuthCredential nor TechCredential, skipping...")
                            i += 1
                else: 
                    i += 1
            else:
                i += 1 
        return result
    except Exception as e:
        print(f"Error checking chained proofs: {e}")
        return {}

# Fetch revocation list from ledger
async def ledger_handler(submitter_did, rev_reg_id, rev_lists):
    print("Fetching revocation list from ledger...")
    response = await get_rev_list(submitter_did, rev_reg_id)

    rev_lists[rev_reg_id] = response
    print("Revocation list attached to revocations lists:", rev_lists, "\n")
    
    return rev_lists

# Reset chained proofs to initial state
def reset_chain(initial_proof, holders):
    chained_proofs = initial_proof.copy()
    print("Reseting chained proofs:", chained_proofs)
    prev_proofs = {}
    print("Reseting prev_proofs:", prev_proofs)
    issuer = next(iter(chained_proofs.values())).get("authorizer_cn")
    holder = next(iter(chained_proofs.values())).get("authorizee_cn")
    holders.clear()
    holders.append(holder)
    print("Reseting issuer:", issuer)
    print("Reseting holders:", holders)

    return chained_proofs, prev_proofs, issuer, holder, holders
