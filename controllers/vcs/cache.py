import time
import json

from .check_revocation import get_rev_list

#proof_cache = {} #memory

# file
with open("vcs/cache.json") as f:
    proof_cache = json.load(f)

CACHE_EXPIRATION_TIME = 300 #86400 # 24 hours 

async def cache_proof(proof_id, did, connection_id, proof_identifiers, proof_data):
    current_time = int(time.time())
    proof_cache[proof_id] = {'did': did, 'connection_id': connection_id, 'identifiers': proof_identifiers, 'data': proof_data, 'timestamp': current_time}
    with open("cache.json", "w") as f:
        json.dump(proof_cache, f)
    print("Proof cached:", proof_cache[proof_id])
    print("Cache:", proof_cache)


def validate_proof(proof_id):
    current_time = time.time()
    if proof_id in proof_cache:
        cached_time = proof_cache[proof_id]['timestamp']

        if current_time - cached_time <= CACHE_EXPIRATION_TIME:
            return True

    return False

async def get_proof(did, submitter_did):
    delete_list = []
    result = {}
    for p in proof_cache.items():
        _, data = p
        if data['did'] == did:
            val = validate_proof(p[0])
            if val == True:
                result[p[0]] = data
            else:
                print("Proof is no longer valid, checking revocation status...", "\n")
                try:
                    cred_rev_id = data["data"]["self_attested_attrs"]["cred_rev_id"]
                    rev_reg = data['identifiers'][0]["rev_reg_id"]
                    response = await get_rev_list(submitter_did, rev_reg, cred_rev_id)
                    if response == True:
                        print("Credential in proof is revoked, ready to remove it from cache...", "\n")
                        delete_list.append(p[0])
                    elif response == False:
                        current_time = int(time.time())
                        print("Credential in proof is not revoked, updating timestamp...", "\n")
                        proof_cache[p[0]]["timestamp"] = current_time
                        with open("vcs/cache.json", "w") as f:
                            json.dump(proof_cache, f)
                        result[p[0]] = data
                except Exception as e:
                    print(f"Error checking revocation status: {e}")

    if delete_list: 
        print("Removing proof cause it is not valid...", "\n")
        delete_proof(delete_list)

    return result

async def get_proofs():
    return proof_cache

def delete_proof(delete_list):
    for proof_id in delete_list:
        if proof_id in proof_cache:
            proof_cache.pop(proof_id, None)

            with open("vcs/cache.json", "w") as f:
                json.dump(proof_cache, f)

            print("Proof removed from cache!", "\n")
    return None
