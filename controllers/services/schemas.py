from aries_cloudcontroller import SchemaPostRequest, SchemaPostOption, AnonCredsSchema

async def get_schemas(client, schema_issuer_did, schema_name, schema_version):
    result = await client.anoncreds_schemas.get_schemas(
        schema_issuer_id = schema_issuer_did,
        schema_name = schema_name,
        schema_version = schema_version
    )
    return result

async def get_schema(client, schema_id):
    result = await client.anoncreds_schemas.get_schema(
        schema_id = schema_id
    )
    return(result)

async def publish_schema(client, issuer_did, attributes, schema_name, schema_version):
    result = await client.anoncreds_schemas.create_schema(
        body =  SchemaPostRequest(
            var_schema = AnonCredsSchema(
                attr_names = attributes, #list
                issuer_id = issuer_did,
                name = schema_name,
                version = schema_version
            )
        )
    )
    return result


