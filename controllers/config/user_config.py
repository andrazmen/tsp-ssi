BASE_URL = "http://localhost:8021"
PORT = 5000
INVITATION = {"accept": ["didcomm/aip1", "didcomm/aip2;env=rfc19"], "alias": "user", "goal": "DID exchange", "goal_code": "did-exchange", "handshake_protocols": ["https://didcomm.org/didexchange/1.1"], "my_label": "user", "protocol_version": "1.1", "use_public_did": True}
SCHEMA_NAME = "AuthCredential"
SCHEMA_VERSION = "1.0.0"
SCHEMA_ATTR = ["issuer_did", "issuer_cn", "issuer_role", "subject_did", "subject_cn", "subject_role", "time_slot", "resource", "resource_type", "actions", "description", "valid_from", "valid_until", "issue_datetime", "credential_type"]
p12_PATH = "/home/andraz/tsp/CA-si/user-certificates/cf0a72fb-2661-4ec2-99f7-95fa3b0b1229.p12"