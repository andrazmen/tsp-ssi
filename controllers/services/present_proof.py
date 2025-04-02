from aries_cloudcontroller import (V20PresProblemReportRequest, V20PresSpecByFormatRequest, IndyPresSpec, IndyRequestedCredsRequestedAttr, V20PresProposalRequest, V20PresProposalByFormat, AnoncredsPresentationRequest, AnoncredsPresentationReqAttrSpec, AnoncredsPresentationRequestNonRevoked, V20PresentationSendRequestToProposal, V20PresSendRequestRequest, V20PresRequestByFormat)

import time

from utils.tools import random_nonce

# Remove an existing presentation exchange record
async def delete_pres_record(client, pres_ex_id):
    result = await client.present_proof_v2_0.delete_record(
        pres_ex_id = pres_ex_id
    )

    return result

# Fetch a single presentation exchange record
async def get_pres_record(client, pres_ex_id):
    result = await client.present_proof_v2_0.get_record(
        pres_ex_id = pres_ex_id
    )

    return result

# Fetch all present-proof exchange record
async def get_pres_records(client, connection_id, role, state):
    result = await client.present_proof_v2_0.get_records(
        connection_id = connection_id,
        #descending,
        #limit,
        #offset,
        #order_by,
        role = role,
        state = state
        #thread_id,
    )

    return result

# Fetch credentials from wallet for presentation request
async def get_matching_credentials(client, pres_ex_id):
    result = await client.present_proof_v2_0.get_matching_credentials(
        pres_ex_id = pres_ex_id,
        #count
        #extra_query
        #limit
        #offset
        #referent
        #start
    )

    return result

# Send a problem report for presentation exchange
async def report_pres_problem(client, pres_ex_id, description):
    result = await client.present_proof_v2_0.report_problem(
        pres_ex_id = pres_ex_id,
        body = V20PresProblemReportRequest(
            description = description
        )
    )

    return result

# Sends a proof presentation
async def send_presentation(client, pres_ex_id, cred_id, cred_rev_id):
    result = await client.present_proof_v2_0.send_presentation(
        pres_ex_id = pres_ex_id,
        body = V20PresSpecByFormatRequest(
            auto_remove = False,
            anoncreds = IndyPresSpec(
                requested_attributes={
                    "auth_attr": IndyRequestedCredsRequestedAttr(
                        cred_id=cred_id, 
                        revealed=True
                    )
                },
                requested_predicates = {}, #IndyRequestedCredsRequestedPred()
                self_attested_attributes = {
                    "cred_rev_id": cred_rev_id
                },
                trace = True
            ),
            #dif
            #indy
            trace = True
        )
    )

    return result

# Sends a presentation proposal
async def send_pres_proposal(client, connection_id, names, schema_name):
    timestamp = int(time.time())
    result = await client.present_proof_v2_0.send_proposal(
        body = V20PresProposalRequest(
            auto_present = False,
            auto_remove = False,
            #comment = comment,
            connection_id = connection_id,
            presentation_proposal = V20PresProposalByFormat(
                anoncreds = AnoncredsPresentationRequest(
                    name = "Proof request",
                    non_revoked = AnoncredsPresentationRequestNonRevoked(
                        var_from = 0,
                        to = timestamp
                    ),
                    nonce = random_nonce(),
                    requested_attributes={
                        "auth_attr": AnoncredsPresentationReqAttrSpec(
                            #name = "time_slot",
                            names=names,
                            non_revoked={"from": 0, "to": timestamp},
                            restrictions = [{
                                "schema_name": schema_name
                            }]
                        ),
                        "cred_rev_id": {
                            "name": "cred_rev_id",
                            "self_attest_allowed": True
                        } 
                    },
                    requested_predicates = {}, #AnoncredsPresentationReqPredSpec
                    version = "1.0"
                )
                #dif
                #indy
            ),
            trace = True
        )
    )

    return result

# Sends a presentation request in reference to a proposal
async def send_pres_request(client, pres_ex_id):
    result = await client.present_proof_v2_0.send_request(
        pres_ex_id = pres_ex_id,
        body = V20PresentationSendRequestToProposal(
            auto_remove = False,
            auto_verify = False,
            trace = True
        )
    )

    return result

# Sends a free presentation request not bound to any proposal
async def send_pres_request_free(client, connection_id, names, schema_name):
    timestamp = int(time.time())
    result = await client.present_proof_v2_0.send_request_free(
        body = V20PresSendRequestRequest(
            auto_remove = False,
            auto_verify = True,
            #comment
            connection_id = connection_id,
            presentation_request = V20PresRequestByFormat(
                anoncreds = AnoncredsPresentationRequest(
                    name = "Proof request",
                    non_revoked = AnoncredsPresentationRequestNonRevoked(
                        var_from = 0,
                        to = timestamp
                    ),
                    nonce = random_nonce(),
                    requested_attributes={
                        "auth_attr": AnoncredsPresentationReqAttrSpec(
                            #name = "time_slot",
                            names = names,
                            non_revoked={"from": 0, "to": timestamp},
                            restrictions = [{
                                "schema_name": schema_name
                            }]
                        ),
                        "cred_rev_id": {
                            "name": "cred_rev_id",
                            "self_attest_allowed": True
                        }                      
                    },
                    requested_predicates = {}, #AnoncredsPresentationReqPredSpec
                    version = "1.0"
                )
                #dif
                #indy
            ),
            trace = True
        )
    )

    return result

# Verify a received presentation
async def verify_presentation(client, pres_ex_id):
    result = await client.present_proof_v2_0.verify_presentation(
        pres_ex_id = pres_ex_id
    )

    return result