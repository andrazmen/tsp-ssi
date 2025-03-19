from aries_cloudcontroller import (V20CredIssueRequest, V20CredExFree, V20CredPreview, V20CredAttrSpec, V20CredFilter, V20CredFilterAnoncreds, V20CredIssueProblemReportRequest, V20CredBoundOfferRequest, V20CredOfferRequest, V20CredRequestRequest, V20CredRequestFree, V20CredFilterLDProof, V20CredStoreRequest)

# Remove an existing credential exchange record
async def delete_record(client, cred_ex_id):
    result = await client.issue_credential_v2_0.delete_record(
        cred_ex_id = cred_ex_id
    )

    return result

# Fetch a single credential exchange record
async def get_record(client, cred_ex_id):
    result = await client.issue_credential_v2_0.get_record(
        cred_ex_id = cred_ex_id
    )

    return result

# Fetch all credential exchange records
async def get_records(client):
    result = await client.issue_credential_v2_0.get_records(
        #connection_id = conn_id,
        #descending,
        #limit,
        #offset,
        #order_by,
        #role,
        #state,
        #thread_id,
    )

    return result

# Send holder a credential
async def issue_credential(client, cred_ex_id):
    result = await client.issue_credential_v2_0.issue_credential(
        cred_ex_id = cred_ex_id
        #body = V20CredIssueRequest(
         #   comment = comment
        #)
    )

    return result

# Send holder a credential (automated)
async def issue_credential_automated(client):
    result = await client.issue_credential_v2_0.issue_credential_automated(
        body = V20CredExFree(
            auto_remove = False,
            comment = comment,
            connection_id = conn_id,
            credential_preview = V20CredPreview(
                type,
                attributes = V20CredAttrSpec(
                    mime_type,
                    name,
                    value
                )
            ),
            filter = V20CredFilter(
                anoncreds = V20CredFilterAnoncreds(
                    cred_def_id,
                    issuer_id,
                    schema_id,
                    schema_issuer_id,
                    schema_name,
                    schema_version
                )
                #indy,
                #ld_proof,
                #vc_di
            ),
            replacement_id,
            trace = True,
            #verification_method
        )
    )

    return result

# Send a problem report for credential exchange
async def report_problem(client, cred_ex_id, description):
    result = await client.issue_credential_v2_0.report_problem(
        cred_ex_id = cred_ex_id,
        body = V20CredIssueProblemReportRequest(
            description = description
        )
    )

    return result

# Send holder a credential offer in reference to a proposal with preview
async def send_offer(client, cred_ex_id, attributes, cred_def_id, issuer_id, schema_id):
    result = await client.issue_credential_v2_0.send_offer(
        cred_ex_id = cred_ex_id,
        body = V20CredBoundOfferRequest(
            counter_preview = V20CredPreview(
                type = "issue-credential/2.0/credential-preview",
                #attributes = [V20CredAttrSpec(
                #    #mime_type,
                #    name = name,
                #    value = value
                #),
                #V20CredAttrSpec(
                #)]
                attributes = attributes
            ),
            filter = V20CredFilter(
                anoncreds = V20CredFilterAnoncreds(
                    cred_def_id = cred_def_id,
                    issuer_id = issuer_id,
                    schema_id = schema_id
                    #schema_issuer_id,
                    #schema_name,
                    #schema_version
                )
                #indy,
                #ld_proof,
                #vc_di
            )
        )
    )

    return result

# Send holder a credential offer, independent of any proposal
async def send_offer_free(client, conn_id, attributes, cred_def_id, issuer_id, schema_id):
    result = await client.issue_credential_v2_0.send_offer_free(
        body = V20CredOfferRequest(
            auto_issue = True,
            auto_remove = False,
            #comment,
            connection_id = conn_id,
            credential_preview = V20CredPreview(
                type = "issue-credential/2.0/credential-preview",
                #attributes = V20CredAttrSpec(
                #    mime_type,
                #    name,
                #    value
                #)
                attributes = attributes
            ),
            filter = V20CredFilter(
                anoncreds = V20CredFilterAnoncreds(
                    cred_def_id,
                    issuer_id,
                    schema_id
                    #schema_issuer_id,
                    #schema_name,
                    #schema_version
                )
                #indy,
                #ld_proof,
                #vc_di
            ),
            #replacement_id,
            trace = True
        )
    )

    return result

# Send issuer a credential proposal
async def send_proposal(client, conn_id, schema_id):
    result = await client.issue_credential_v2_0.send_proposal(
        body = V20CredExFree(
            auto_remove = False,
            #comment = comment,
            connection_id = conn_id,
            #credential_preview = V20CredPreview(
                #type,
                #attributes = V20CredAttrSpec(
                    #mime_type,
                    #name,
                    #value
                #)
            #),
            filter = V20CredFilter(
                anoncreds = V20CredFilterAnoncreds(
                    #cred_def_id,
                    #issuer_id,
                    schema_id
                    #schema_issuer_id,
                    #schema_name
                    #schema_version
                )
                #indy,
                #ld_proof,
                #vc_di
            ),
            #replacement_id,
            trace = True,
            #verification_method
        )
    )

    return result

# Send issuer a credential request
async def send_request(client, cred_ex_id, holder_did):
    result = await client.issue_credential_v2_0.send_request(
        cred_ex_id = cred_ex_id,
        body = V20CredRequestRequest(
            auto_remove = False,
            holder_did = holder_did
        )
    )

    return result

# Send issuer a credential request not bound to an existing thread. Indy credentials cannot start at a request
"""
async def send_request_free(client):
    result = await client.issue_credential_v2_0.send_request_free(
        body = V20CredRequestFree(
            auto_remove = False,
            comment,
            connection_id,
            filter = V20CredFilterLDProof(
                ld_proof = LDProofVCDetail(

                )
            ),
            holder_did,
            trace = True
        )
    )

    return result

"""
# Store a received credential
async def store_credential(client):
    result = await client.issue_credential_v2_0.store_credential(
        cred_ex_id,
        body = V20CredStoreRequest(
            credential_id
        )
    )

    return result