import time

proof_cache = {}

CACHE_EXPIRATION_TIME = 86400 

def cache_proof(proof_id, connection_id, proof_data):
    current_time = time.time()
    proof_cache[proof_id] = {'connection_id': connection_id, 'data': proof_data, 'timestamp': current_time}
    print("Proof cached:", proof_cache[proof_id])


def validate_proof(proof_id):
    current_time = time.time()
    if proof_id in proof_cache:
        cached_time = proof_cache[proof_id]['timestamp']

        if current_time - cached_time <= CACHE_EXPIRATION_TIME:
            return True

    return False

def get_proof(proof_id):
    if proof_id in proof_cache:
        return proof_cache[proof_id]['data']
    return None

def delete_proof(proof_id):
    if proof_id in proof_cache:
        proof_cache.pop(proof_id, None)

        print("Proof deleted from cache!")
        return None
    return None
        
cache_proof(1, "aba-asd", {'a': 'a', 'b': 'b'})
print(proof_cache)
delete_proof(1)
print(proof_cache)