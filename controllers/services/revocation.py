from aries_cloudcontroller import RevokeRequestSchemaAnoncreds

async def get_active_rev_reg(client, cred_def_id):
    result = await client.anoncreds_revocation.get_active_revocation_registry(
        cred_def_id = cred_def_id
    )

    return result

async def get_rev_reg_issued(client, rev_reg_id):
    result = await client.anoncreds_revocation.get_rev_reg_issued_count(
        rev_reg_id = rev_reg_id
    )

    return result

async def get_rev_reg_issued_details(client, rev_reg_id):
    result = await client.anoncreds_revocation.get_rev_reg_issued_details(
        rev_reg_id = rev_reg_id
    )

    return result

async def get_rev_regs(client, cred_def_id):
    result = await client.anoncreds_revocation.get_revocation_registries(
        cred_def_id = cred_def_id
        #state
    )

    return result

async def get_rev_reg(client, rev_reg_id):
    result = await client.anoncreds_revocation.get_revocation_registry(
        rev_reg_id = rev_reg_id
        #state
    )

    return result

async def revoke(client, comment, conn_id, cred_ex_id, thread_id):
    result = await client.anoncreds_revocation.revoke(
        body = RevokeRequestSchemaAnoncreds(
            comment = comment,
            connection_id = conn_id,
            cred_ex_id = cred_ex_id, # ALI TA ALI cred-rev_id in rev_reg_id
            #cred_rev_id = cred_rev_id,
            notify = True,
            notify_version = "v1.0",
            publish = True, 
            #rev_reg_id = rev_reg_id,
            thread_id = thread_id
        )
    )

    return result