import time
import json

from aiocache import cached

from .check_revocation import get_rev_list

#@cached(ttl=60)
async def get_proofs(records, requester_cn, submitter_did, topics):
    rev_lists = {}
    result = {} 
    recs = records.copy()   
    try:
        for r in recs:
            print("Get proof:", r["pres_ex_id"])
            values = r["by_format"]["pres"]["anoncreds"]["requested_proof"]["revealed_attr_groups"]["auth_attr"]["values"]
            subject = values.get("subject_cn")
            authorizee = values.get("authorizee_cn")
            if (subject and requester_cn == subject.get("raw")) or (authorizee and requester_cn == authorizee.get("raw")):
                pres_ex_id = r["pres_ex_id"]
                cred_rev_id = r["by_format"]["pres"]["anoncreds"]["requested_proof"]["self_attested_attrs"]["cred_rev_id"]
                rev_reg_id = r["by_format"]["pres"]["anoncreds"]["identifiers"][0]["rev_reg_id"]

                if rev_reg_id not in rev_lists:
                    rev_lists = await ledger_handler(submitter_did, rev_reg_id, rev_lists)
                if cred_rev_id in rev_lists[rev_reg_id]:
                    print(f"Credential with cred_rev_id {cred_rev_id} is revoked!", "\n")
                    continue
                else:
                    print(f"Credential in proof {r["pres_ex_id"]} is valid!", "\n")
                    pres_ex_id = r["pres_ex_id"]

                    result_item = {}
                    if values.get("credential_type").get("raw") == "technical":
                        print("Credential type is TechCredential!")
                        result_item[pres_ex_id] = {"issuer_cn": values.get("issuer_cn").get("raw"), "issuer_did": values.get("issuer_did").get("raw"), "subject_cn": values.get("subject_cn").get("raw"), "subject_did": values.get("subject_did").get("raw"), "data": values, "identifiers": r["by_format"]["pres"]["anoncreds"]["identifiers"]}
                        result[len(result) + 1] = result_item
                        #return result
                    elif (values.get("credential_type").get("raw") == "authorization") and (values.get("topics").get("raw") in topics):
                        print("Credential type is not TechCredential, checking chained proofs...")
                        result_item[pres_ex_id] = {"authorizer_cn": values.get("authorizer_cn").get("raw"), "authorizer_did": values.get("authorizer_did").get("raw"), "authorizee_cn": values.get("authorizee_cn").get("raw"), "authorizee_did": values.get("authorizee_did").get("raw"), "data": values, "identifiers": r["by_format"]["pres"]["anoncreds"]["identifiers"]}
                        proofs = await check_chain(records, result_item, rev_lists, submitter_did, topics)
                        if proofs:
                            result[len(result) + 1] = proofs
        return result
    except Exception as e:
            print(f"Error getting proofs: {e}")
            return {}  

async def check_chain(records, initial_proofs, rev_lists, submitter_did, topics):
    chained_proofs = initial_proofs.copy()
    prev_proof = {}
    recs = records.copy()
    #participants = {"issuers": [], "holders": []}
    issuers = []
    value = next(iter(chained_proofs.values()))
    issuer = value.get("authorizer_cn")
    #holder = value.get("authorizee_cn")
    #participants["issuers"].append(issuer)
    #participants["holders"].append(holder)
    loop_proofs = []
    
    i = 0
    while i < len(recs):
        if recs[i]["pres_ex_id"] not in loop_proofs:
            print("runda:", i)
            r = recs[i]
            print("Check chain:", r["pres_ex_id"])
            values = r["by_format"]["pres"]["anoncreds"]["requested_proof"]["revealed_attr_groups"]["auth_attr"]["values"]
            subject = values.get("subject_cn")
            authorizee = values.get("authorizee_cn")
            authorizer = values.get("authorizer_cn")
            tech_issuer = values.get("issuer_cn")
            if (subject and issuer == subject.get("raw")) or (authorizee and issuer == authorizee.get("raw")):
                #if (authorizer and (authorizer.get("raw") in participants["issuers"]) and (authorizee.get("raw") in participants["holders"])) or (tech_issuer and (tech_issuer.get("raw") in participants["issuers"]) and (subject.get("raw") in participants["holders"])):
                if (authorizee and (authorizee.get("raw") in issuers)) or (subject and (subject.get("raw") in issuers)):
                    print("Loop detected, skipping...")
                    loop_proofs.append(next(iter(prev_proof)))
                    print("Loop proofs:", loop_proofs)

                    # RESET
                    issuers = []
                    prev_proof = {}
                    chained_proofs = initial_proofs.copy()
                    value = next(iter(chained_proofs.values()))
                    issuer = value.get("authorizer_cn")
                    i = 0
                    continue
                if prev_proof != {}:
                    chained_proofs.update(prev_proof)
                    data = next(iter(prev_proof.values()))
                    prev_issuer = data.get("authorizer_cn")
                    issuers.append(prev_issuer)
                    print("TO SO ISSUERS:", issuers)
                    prev_proof = {}
                cred_rev_id = r["by_format"]["pres"]["anoncreds"]["requested_proof"]["self_attested_attrs"]["cred_rev_id"]
                rev_reg_id = r["by_format"]["pres"]["anoncreds"]["identifiers"][0]["rev_reg_id"]
                #if rev_reg_id not in rev_lists:
                    #rev_lists = await ledger_handler(submitter_did, rev_reg_id, rev_lists)
                #rev_lists[rev_reg_id] = [1,2,3,4,5,6,7,8]
                #if cred_rev_id in rev_lists[rev_reg_id]:
                print(cred_rev_id)
                if cred_rev_id in ["3"]:
                    print(f"Credential with cred_rev_id {cred_rev_id} is revoked!", "\n")
                    i += 1
                else:
                    print(f"Credential in proof {r["pres_ex_id"]} is valid!", "\n")
                    pres_ex_id = r["pres_ex_id"]

                    if values.get("credential_type").get("raw") == "technical":
                        print("Credential type is TechCredential!")
                        chained_proofs[pres_ex_id] = {"issuer_cn": values.get("issuer_cn").get("raw"), "issuer_did": values.get("issuer_did").get("raw"), "subject_cn": values.get("subject_cn").get("raw"), "subject_did": values.get("subject_did").get("raw"), "data": values, "identifiers": r["by_format"]["pres"]["anoncreds"]["identifiers"]}
                        return chained_proofs
                    elif (values.get("credential_type").get("raw") == "authorization") and (values.get("topics").get("raw") in topics):
                        print("Credential type is not TechCredential, checking proofs...")
                        prev_proof[pres_ex_id] = {"authorizer_cn": values.get("authorizer_cn").get("raw"), "authorizer_did": values.get("authorizer_did").get("raw"), "authorizee_cn": values.get("authorizee_cn").get("raw"), "authorizee_did": values.get("authorizee_did").get("raw"), "data": values, "identifiers": r["by_format"]["pres"]["anoncreds"]["identifiers"]}
                        issuer = values.get("authorizer_cn").get("raw")
                        #holder = values.get("authorizee_cn").get("raw")
                        #participants["issuers"].append(issuer)
                        #participants["holders"].append(holder)
                        #print("TO SO PARTICIPANTS:", participants)
                        i = 0
            else: 
                i += 1
        else:
            i += 1 
    chained_proofs = {}
    return chained_proofs

async def ledger_handler(submitter_did, rev_reg_id, rev_lists):
    print("Fetching revocation list from ledger...")
    response = await get_rev_list(submitter_did, rev_reg_id)

    rev_lists[rev_reg_id] = response
    print("Revocation list attached to revocations lists:", rev_lists, "\n")
    
    return rev_lists



"""async def get_proof(submitter_did, did, records):
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
                print("Credential in proof is valid!", "\n")
                result[pres_ex_id] = {"did": did, "connection_id": r["connection_id"], "data": r["by_format"]["pres"]["anoncreds"]["requested_proof"], "identifiers": r["by_format"]["pres"]["anoncreds"]["identifiers"]}
        except Exception as e:
            print(f"Error checking credentials revocation status: {e}")  
    
    return result
"""