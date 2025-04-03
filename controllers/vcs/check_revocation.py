from indy_vdr import pool, ledger, bindings
from indy_vdr.resolver import Resolver

import time

async def get_rev_list(did, rev_reg, cred_rev_id):
    try: 
        timestamp = int(time.time())

        # Create a pool handle to connect to the von-network ledger
        pool_handle = await pool.open_pool("vcs/utils/genesis.txt")
        
        rev_list_req = ledger.build_get_revoc_reg_delta_request(did, rev_reg, 0, timestamp)

        response = await pool_handle.submit_request(rev_list_req)

        revoked_list = response["data"]["value"]["revoked"]
        print("Revoked credentials list:", revoked_list, "\n")

        for c in revoked_list:
            if str(c) == cred_rev_id:
                print(f"Credential with cred_rev_id {cred_rev_id} is revoked!", "\n")
                return True

        return False

    except Exception as e:
        print(f"Error getting revocation list: {e}")