## Authorization Credential

**AuthCred offer request (message):** {"id": "fcc931cf-8ed2-4a18-95b6-daca83a31894", "type": "offer_request", "cred_type": "authorization"}

**Auth schema, proof request or proof proposal (names) attributes:** 
["authorizer_did", "authorizer_cn", "authorizer_role", "authorizee_did", "authorizee_cn", "authorizee_role", "power_consumption", "power_forecast", "flexibility", "time_slot", "topics", "actions", "description", "issue_datetime", "authorization_start", "authorization_end", "credential_type"]

**Auth offer attributes:** 
{"authorizer_did": "did:sov:VWJgMNS75SWMpkp2gT74Zq", "authorizer_cn": "cf0a72fb-2661-4ec2-99f7-95fa3b0b1229", "authorizer_role": "user", "authorizee_did": "did:sov:KNQMNG77kewjDqW15syTXT", "authorizee_cn": "fcc931cf-8ed2-4a18-95b6-daca83a31894", "authorizee_role": "aggregator", "power_consumption": "10462", "power_forecast": "12697", "flexibility": "500", "time_slot": ["monday", "friday", "sunday"], "topics": ["/cem/5efff1f7-7b0f-47e0-bf25-3055ca8e7fe8/rm/96439751-b2ad-496b-b80e-a3cb4e79b0db/devices", "/cem/5efff1f7-7b0f-47e0-bf25-3055ca8e7fe8/rm/96439751-b2ad-496b-b80e-a3cb4e79b0db/control"], "actions": ["read", "subscribe"], "description": "test credential", "issue_datetime": "2025-05-30T13:54:59+00:00", "authorization_start": "2025-06-01T13:54:59+00:00", "authorization_end": "2025-12-31T13:54:59+00:00", "credential_type": "authorization"}

## Certificate Credential

**Cert schema, proof request or proof proposal (names) attributes:** ["operator_did", "operator_name", "operator_type", "operator_contact", "subject_did", "subject_name", "subject_role", "subject_device_id", "subject_device_type", "description", "issue_datetime", "credential_type"]

**Cert offer attributes:** {"operator_did": "did:sov:KNQMNG77kewjDqW15syTXT", "operator_name": "ECE d.o.o.", "operator_type": "provider", "operator_contact": "info@ece.si", "subject_did": "did:sov:3UGHodegK6FFatbMgCJQnU", "subject_name": "agg_e5D1Gyvz9Y", "subject_role": "aggregator", "subject_device_id": "", "subject_device_type": "", "description": "", "issue_datetime": "2025-03-03T13:00:00Z", "credential_type": "certificate"}

## Technical Credential

**TechCred offer request (message):** {"id": "cf0a72fb-2661-4ec2-99f7-95fa3b0b1229", "type": "offer_request", "cred_type": "technical"}

**Tech schema, proof request or proof proposal (names) attributes:** 
["issuer_did", "issuer_cn", "issuer_role", "subject_did", "subject_cn", "subject_role", "subject_device_id", "subject_device_type", "cem_id", "hems_id", "description", "issue_datetime", "credential_type"]

**Tech offer attributes:** {"issuer_did": "did:sov:E56xjJ1frUaQUr47sN14nn", "issuer_cn": "47658be9-6964-4565-a3a3-4abbe9b60da1", "issuer_role": "technical aggregator", "subject_did": "did:sov:VWJgMNS75SWMpkp2gT74Zq", "subject_cn": "cf0a72fb-2661-4ec2-99f7-95fa3b0b1229", "subject_role": "user", "subject_device_id": "383456780018747622", "subject_device_type": "ZCXI120CPU1L1D1", "cem_id": "5efff1f7-7b0f-47e0-bf25-3055ca8e7fe8", "hems_id": "1.2.826.0.1.3680043.2.1125.3.2.105", "description": "test credential", "issue_datetime": "2025-05-30T13:50:59+00:00", "credential_type": "technical"}

**Time format (UTC, ISO8601):**
print(datetime.now(timezone.utc).replace(microsecond=0).isoformat())