## Service Credential
**Schema, proof request or proof proposal attrs:**
["issuer_did", "issuer_cn", "issuer_role", "subject_did", "subject_cn", "subject_role", "time_slot", "resource", "resource_type", "actions", "description", "valid_from", "valid_until", "issue_datetime", "credential_type"]

## Authorization Credential

**AuthCred offer request (message):** {"certificate": "", "resource": "/CEM/5efff1f7-7b0f-47e0-bf25-3055ca8e7fe8/RM/96439751-b2ad-496b-b80e-a3cb4e79b0db/telemetry", "action": ["read", "subscribe"], "time_slot": ["monday", "friday", "sunday"], "cred_type": "authorization", "message_type": "offer_request"}

**Auth offer attributes:** 
{"issuer_did": "did:sov:VWJgMNS75SWMpkp2gT74Zq", "issuer_cn": "cf0a72fb-2661-4ec2-99f7-95fa3b0b1229", "issuer_role": "end_user", "subject_did": "did:sov:KNQMNG77kewjDqW15syTXT", "subject_cn": "fcc931cf-8ed2-4a18-95b6-daca83a31894", "subject_role": "aggregator", "time_slot": ["monday", "friday", "sunday"], "resource": "/CEM/5efff1f7-7b0f-47e0-bf25-3055ca8e7fe8/RM/96439751-b2ad-496b-b80e-a3cb4e79b0db/telemetry", "resource_type": "topic", "actions": ["read", "subscribe"], "description": "test credential", "valid_from": "2025-07-07T09:54:59+00:00", "valid_until": "2025-12-31T13:54:59+00:00", "issue_datetime": "2025-07-22T09:29:10+00:00", "credential_type": "authorization"}

Napačen did:
{"issuer_did": "did:sov:VWJgMNS75SWMpkp2gT74Zq", "issuer_cn": "cf0a72fb-2661-4ec2-99f7-95fa3b0b1229", "issuer_role": "end_user", "subject_did": "did:sov:KNQMNG77kewjDqW15sy", "subject_cn": "fcc931cf-8ed2-4a18-95b6-daca83a31894", "subject_role": "aggregator", "time_slot": ["monday", "friday", "sunday"], "resource": "/cem/5efff1f7-7b0f-47e0-bf25-3055ca8e7fe8/rm/96439751-b2ad-496b-b80e-a3cb4e79b0db/devices", "resource_type": "topic", "actions": ["read", "subscribe"], "description": "test credential", "valid_from": "2025-06-01T13:54:59+00:00", "valid_until": "2025-12-31T13:54:59+00:00", "issue_datetime": "2025-05-30T13:54:59+00:00", "credential_type": "authorization"}

Napačen authorizer (ni verige):
{"issuer_did": "did:sov:VWJgMNS75SWMpkp2gT74Zq", "issuer_cn": "cf0a72fb-2661-4ec2-99f7-95fa3b0b1", "issuer_role": "end_user", "subject_did": "did:sov:KNQMNG77kewjDqW15syTXT", "subject_cn": "fcc931cf-8ed2-4a18-95b6-daca83a31894", "subject_role": "aggregator", "time_slot": ["monday", "friday", "sunday"], "resource": "/cem/5efff1f7-7b0f-47e0-bf25-3055ca8e7fe8/rm/96439751-b2ad-496b-b80e-a3cb4e79b0db/devices", "resource_type": "topic", "actions": ["read", "subscribe"], "description": "test credential", "valid_from": "2025-06-01T13:54:59+00:00", "valid_until": "2025-12-31T13:54:59+00:00", "issue_datetime": "2025-05-30T13:54:59+00:00", "credential_type": "authorization"}

## Certificate Credential
**TechCred offer request (message):** {"certificate": "", "resource": "smart_meter/383456780018747622", "action": ["read", "write"], "time_slot": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"], "cred_type": "certificate", "message_type": "offer_request"}

**Cert offer attributes:** 
{"issuer_did": "did:sov:3UGHodegK6FFatbMgCJQnU", "issuer_cn": "", "issuer_role": "edo", "subject_did": "did:sov:VWJgMNS75SWMpkp2gT74Zq", "subject_cn": "cf0a72fb-2661-4ec2-99f7-95fa3b0b1229", "subject_role": "end_user", "time_slot": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"], "resource": "smart_meter/383456780018747622", "resource_type": "smart_meter", "actions": ["read", "write"], "description": "test credential", "valid_from": "2025-06-01T13:54:59+00:00", "valid_until": "2025-12-31T13:54:59+00:00", "issue_datetime": "2025-05-30T13:54:59+00:00", "credential_type": "certificate"}

## Technical Credential

**TechCred offer request (message):** {"certificate": "", "resource": "CEM/5efff1f7-7b0f-47e0-bf25-3055ca8e7fe8/HEMS/1.2.826.0.1.3680043", "action": ["read", "write"], "time_slot": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"], "cred_type": "technical", "message_type": "offer_request"}

**Tech offer attributes:** 
{"issuer_did": "did:sov:E56xjJ1frUaQUr47sN14nn", "issuer_cn": "47658be9-6964-4565-a3a3-4abbe9b60da1", "issuer_role": "technical_aggregator", "subject_did": "did:sov:VWJgMNS75SWMpkp2gT74Zq", "subject_cn": "cf0a72fb-2661-4ec2-99f7-95fa3b0b1229", "subject_role": "end_user", "time_slot": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"], "resource": "CEM/5efff1f7-7b0f-47e0-bf25-3055ca8e7fe8/HEMS/1.2.826.0.1.3680043", "resource_type": "cem:hems", "actions": ["subscribe", "read", "write"], "description": "test credential", "valid_from": "2025-07-07T09:54:59+00:00", "valid_until": "2025-12-31T13:54:59+00:00", "issue_datetime": "2025-07-22T08:54:59+00:00", "credential_type": "technical"}

**Time format (UTC, ISO8601):**
print(datetime.now(timezone.utc).replace(microsecond=0).isoformat())