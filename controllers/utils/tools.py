import base64
import json
import random
from urllib.parse import urlparse, parse_qs

from aries_cloudcontroller import V20CredAttrSpec

def decode(enc_str):
    try:
        missing_padding = len(enc_str) % 4
        if missing_padding:
            enc_str += '=' * (4 - missing_padding)
            
        base64_str = enc_str
        base64_bytes = base64_str.encode('ascii')

        enc_str_bytes = base64.b64decode(base64_bytes)
        dec_str = enc_str_bytes.decode('ascii')

        print(f"Decoded: {dec_str}", "\n") 
        return dec_str
    except Exception as e:    
        print(f"Error decoding: {e}")
               

def extract_oob(url):
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        oob_value = query_params.get("oob", [None])[0]
        print(f"Extracted OOB: {oob_value}", "\n")
        return oob_value
    except Exception as e:
        print(f"Error extracting OOB: {e}")

"""
decode(extract_oob("http://localhost:8020?oob=eyJAdHlwZSI6ICJodHRwczovL2RpZGNvbW0ub3JnL291dC1vZi1iYW5kLzEuMS9pbnZpdGF0aW9uIiwgIkBpZCI6ICIwNTk2OWIzNC0yNWYxLTRkZDQtYmI1ZS1kYjllMjY1Y2M2ZTYiLCAibGFiZWwiOiAiSW52aXRhdGlvbiBmb3IgRElEIGV4Y2hhbmdlIiwgImhhbmRzaGFrZV9wcm90b2NvbHMiOiBbImh0dHBzOi8vZGlkY29tbS5vcmcvZGlkZXhjaGFuZ2UvMS4xIl0sICJhY2NlcHQiOiBbImRpZGNvbW0vYWlwMSIsICJkaWRjb21tL2FpcDI7ZW52PXJmYzE5Il0sICJzZXJ2aWNlcyI6IFsiZGlkOnNvdjpXRmtRdW1XejlvazZVWEVLUDQ5NlVBIl19"))

"""

def json_to_offer_attr(attr_json):
    try:
        attr_dict = json.loads(attr_json)
        
        attr_list = [
            V20CredAttrSpec(name=key, value=value) 
            for key, value in attr_dict.items()
        ]
        return attr_list
    except Exception as e:
        print(f"Error converting json to list: {e}")

def random_nonce():
    first_digit = str(random.randint(1, 9))  # First digit must be 1-9
    other_digits = ''.join(str(random.randint(0, 9)) for _ in range(10))

    return first_digit + other_digits