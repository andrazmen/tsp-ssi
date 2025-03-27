**Schema attributes:** ["authorizer_id", "authorizer_role", "authorizee_id", "authorizee_role", "power_consumption", "power_forecast", "flexibility", "time_slot", "control_type", "description", "issue_datetime", "authorization_start", "authorization_end", "credential_type"]

**Offer attributes:** [{"name": "authorizer_id", "value": "did:sov:WFkQumWz9ok6UXEKP496UA"}, {"name": "authorizer_role", "value": "CEM"}, {"name": "authorizee_id", "value": "did:sov:KzW7Y2H3yVdfJwicwPyreo"}, {"name": "authorizee_role", "value": "aggregator"}, {"name": "power_consumption", "value": "10462"}, {"name": "power_forecast", "value": "12697"}, {"name": "flexibility", "value": "500"}, {"name": "time_slot", "value": "monday"}, {"name": "control_type", "value": "power-profile-based-control"}, {"name": "description", "value": ""}, {"name": "issue_datetime", "value": "2025-03-24T13:00:00Z"}, {"name": "authorization_start", "value": "2025-03-25T12:00:00Z"}, {"name": "authorization_end", "value": "2025-04-25T12:00:00Z"}, {"name": "credential_type", "value": "Authorization Credential"}]

**Offer attributes:** ["did:sov:WFkQumWz9ok6UXEKP496UA", "CEM", "did:sov:KzW7Y2H3yVdfJwicwPyreo", "aggregator", "10462", "12697", "500", "monday", "power-profile-based-control", "", "2025-03-24T13:00:00Z", "2025-03-25T12:00:00Z", "2025-04-25T12:00:00Z", "Authorization Credential"]

**Proof request or proposal (names)** ["authorizer_id", "authorizer_role", "authorizee_id", "authorizee_role", "power_consumption", "power_forecast", "flexibility", "time_slot", "control_type", "description", "issue_datetime", "authorization_start", "authorization_end", "credential_type"]

**Invitation request:**         body=InvitationCreateRequest(
            accept = ["didcomm/aip1", "didcomm/aip2;env=rfc19"],
            alias = "test1",
            goal = "DID exchange", 
            goal_code = "did-exchange",
            handshake_protocols = ["https://didcomm.org/didexchange/1.1"],
            #mediation_id,
            #meta_data,
            my_label = "Invitation for DID exchange",
            protocol_version = "1.1",
            #use_did,
            #use_did_method,
            use_public_did = True
        )

**Offer attributes:** {"authorizer_id": "did:sov:WFkQumWz9ok6UXEKP496UA", "authorizer_role": "CEM", "authorizee_id": "did:sov:KzW7Y2H3yVdfJwicwPyreo", "authorizee_role": "aggregator", "power_consumption": "10462", "power_forecast": "12697", "flexibility": "500", "time_slot": "monday", "control_type": "power-profile-based-control", "description": "", "issue_datetime": "2025-03-24T13:00:00Z", "authorization_start": "2025-03-25T12:00:00Z", "authorization_end": "2025-04-25T12:00:00Z", "credential_type": "Authorization Credential"}