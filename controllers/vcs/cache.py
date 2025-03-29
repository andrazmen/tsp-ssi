import time

proof_cache = {}

CACHE_EXPIRATION_TIME = 86400 

def cache_proof(proof_id, did, connection_id, proof_data):
    current_time = time.time()
    proof_cache[proof_id] = {'did': did, 'connection_id': connection_id, 'data': proof_data, 'timestamp': current_time}
    print("Proof cached:", proof_cache[proof_id])
    print("Cache:", proof_cache)


def validate_proof(proof_id):
    current_time = time.time()
    if proof_id in proof_cache:
        cached_time = proof_cache[proof_id]['timestamp']

        if current_time - cached_time <= CACHE_EXPIRATION_TIME:
            return True

    return False

def get_proof(did):
    delete_list = []
    result = {}
    for p in proof_cache.items():
        print(p)
        _, data = p
        if data['did'] == did:
            val = validate_proof(p[0])
            if val == True:
                result[p[0]] = data
            else:
                delete_list.append(p[0])
                print(delete_list)
    if delete_list: 
        print("Deleting proof cause it is not valid")
        delete_proof(delete_list)
    print(result)
    return result

def get_proofs():
    return proof_cache

def delete_proof(delete_list):
    for proof_id in delete_list:
        if proof_id in proof_cache:
            proof_cache.pop(proof_id, None)

            print("Proof deleted from cache!")
    return None

"""
# TEST        
cache_proof(1, "qwer", "aba-asd", {'a': 'a', 'b': 'b'})
cache_proof(2, "ertz", "bas-kjh", {'c': 'c', 'd': 'd'})
cache_proof(3, "tzui", "lkl-qwe", {'e': 'e', 'f': 'f'})
cache_proof(4, "ertz", "uiz-poi", {'g': 'gc', 'h': 'h'})
print(proof_cache)
get_proof("ertz")
print(proof_cache)
"""