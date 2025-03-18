from aries_cloudcontroller import CredDefPostRequest, InnerCredDef, CredDefPostOptions

async def get_cred_def(client, cred_def_id):
    result = await client.anoncreds_credential_definitions.get_credential_definition(
        cred_def_id = cred_def_id
    )

    return result

async def get_cred_defs(client, issuer_id, schema_id, schema_name, schema_version):
    result = await client.anoncreds_credential_definitions.get_credential_definitions(
        issuer_id = issuer_id,
        schema_id = schema_id,
        schema_name = schema_id,
        schema_version = schema_version
    )

    return result

async def create_cred_def(client, issuer_id, schema_id):
    print(issuer_id, schema_id)
    result = await client.anoncreds_credential_definitions.create_credential_definition(
        body = CredDefPostRequest(
            credential_definition = InnerCredDef(
                issuer_id = issuer_id,
                schema_id = schema_id,
                tag = "default"
            ),
            options = CredDefPostOptions(
               #create_transaction_for_endorser,
               #endorser_connection_id,
               revocation_registry_size = 1000,
               support_revocation = True 
            )
        )
    )

    return result