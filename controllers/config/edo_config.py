BASE_URL = "http://localhost:8041"
PORT = 5100
INVITATION = {"accept": ["didcomm/aip1", "didcomm/aip2;env=rfc19"], "alias": "EDO", "goal": "DID exchange", "goal_code": "did-exchange", "handshake_protocols": ["https://didcomm.org/didexchange/1.1"], "my_label": "EDO", "protocol_version": "1.1", "use_public_did": True}
SCHEMA_NAME = "CertCredential"
SCHEMA_VERSION = "1.0.0"
SCHEMA_ATTR = ["issuer_did", "issuer_cn", "issuer_role", "subject_did", "subject_cn", "subject_role", "time_slot", "resource", "resource_type", "actions", "description", "valid_from", "valid_until", "issue_datetime", "credential_type"]
p12_PATH = "/home/andraz/tsp/CA-si/user-certificates/7c623cc0-c01a-4bdb-bb1b-1c752e974332.p12"
