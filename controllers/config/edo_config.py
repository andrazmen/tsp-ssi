base_url = "http://localhost:8041"
port = 5100
invitation = {"accept": ["didcomm/aip1", "didcomm/aip2;env=rfc19"], "alias": "EDO", "goal": "DID exchange", "goal_code": "did-exchange", "handshake_protocols": ["https://didcomm.org/didexchange/1.1"], "my_label": "EDO", "protocol_version": "1.1", "use_public_did": True}
schema_name = "CertCredential"
schema_version = "1.0.0"
schema_attr = ["operator_id", "operator_name", "operator_type", "operator_contact", "subject_id", "subject_name", "subject_role", "subject_device_id", "subject_device_type", "description", "issue_datetime"]
