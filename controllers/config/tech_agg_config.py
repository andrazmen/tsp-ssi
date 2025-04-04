base_url = "http://localhost:8051"
port = 5150
invitation = {"accept": ["didcomm/aip1", "didcomm/aip2;env=rfc19"], "alias": "ta", "goal": "DID exchange", "goal_code": "did-exchange", "handshake_protocols": ["https://didcomm.org/didexchange/1.1"], "my_label": "ta", "protocol_version": "1.1", "use_public_did": True}
schema_name = "TechCredential"
schema_version = "1.0.0"
schema_attr = ["subject_id", "subject_name", "subject_role", "subject_device_id", "subject_device_type", "hems_id", "description", "issue_datetime"]