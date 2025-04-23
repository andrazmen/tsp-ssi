BASE_URL = "http://localhost:8051"
PORT = 5150
INVITATION = {"accept": ["didcomm/aip1", "didcomm/aip2;env=rfc19"], "alias": "ta", "goal": "DID exchange", "goal_code": "did-exchange", "handshake_protocols": ["https://didcomm.org/didexchange/1.1"], "my_label": "ta", "protocol_version": "1.1", "use_public_did": True}
SCHEMA_NAME = "TechCredential"
SCHEMA_VERSION = "1.0.0"
SCHEMA_ATTR = ["issuer_did", "issuer_cn", "issuer_role", "subject_did", "subject_cn", "subject_role", "subject_device_id", "subject_device_type", "hems_id", "description", "issue_datetime", "credential_type"]
p12_PATH = "/home/andraz/tsp/CA-si/user-certificates/47658be9-6964-4565-a3a3-4abbe9b60da1.p12"