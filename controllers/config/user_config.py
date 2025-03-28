base_url = "http://localhost:8021"
port = 5000
invitation = {"accept": ["didcomm/aip1", "didcomm/aip2;env=rfc19"], "alias": "user", "goal": "DID exchange", "goal_code": "did-exchange", "handshake_protocols": ["https://didcomm.org/didexchange/1.1"], "my_label": "user", "protocol_version": "1.1", "use_public_did": True}
schema_name = "AuthCredential"
schema_version = "1.0.0"
schema_attr = ["authorizer_id", "authorizer_role", "authorizee_id", "authorizee_role", "power_consumption", "power_forecast", "flexibility", "time_slot", "control_type", "description", "issue_datetime", "authorization_start", "authorization_end", "credential_type"]