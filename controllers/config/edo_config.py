BASE_URL = "http://localhost:8041"
PORT = 5100
INVITATION = {"accept": ["didcomm/aip1", "didcomm/aip2;env=rfc19"], "alias": "EDO", "goal": "DID exchange", "goal_code": "did-exchange", "handshake_protocols": ["https://didcomm.org/didexchange/1.1"], "my_label": "EDO", "protocol_version": "1.1", "use_public_did": True}
SCHEMA_NAME = "CertCredential"
SCHEMA_VERSION = "1.0.0"
SCHEMA_ATTR = ["operator_did", "operator_name", "operator_type", "operator_contact", "subject_did", "subject_name", "subject_role", "subject_device_id", "subject_device_type", "description", "issue_datetime", "credential_type"]
