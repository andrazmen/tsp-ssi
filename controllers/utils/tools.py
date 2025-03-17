import base64
from urllib.parse import urlparse, parse_qs

def decode(enc_str):
    base64_str = enc_str
    base64_bytes = base64_str.encode('ascii')

    enc_str_bytes = base64.b64decode(base64_bytes)
    dec_str = enc_str_bytes.decode('ascii')

    print(f"Decoded: {dec_str}", "\n") 
    return dec_str

def extract_oob(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    oob_value = query_params.get("oob", [None])[0]
    print(f"Extracted OOB: {oob_value}", "\n")
    return oob_value

"""
decode(extract_oob("http://localhost:8020?oob=eyJAdHlwZSI6ICJodHRwczovL2RpZGNvbW0ub3JnL291dC1vZi1iYW5kLzEuMS9pbnZpdGF0aW9uIiwgIkBpZCI6ICIwNTk2OWIzNC0yNWYxLTRkZDQtYmI1ZS1kYjllMjY1Y2M2ZTYiLCAibGFiZWwiOiAiSW52aXRhdGlvbiBmb3IgRElEIGV4Y2hhbmdlIiwgImhhbmRzaGFrZV9wcm90b2NvbHMiOiBbImh0dHBzOi8vZGlkY29tbS5vcmcvZGlkZXhjaGFuZ2UvMS4xIl0sICJhY2NlcHQiOiBbImRpZGNvbW0vYWlwMSIsICJkaWRjb21tL2FpcDI7ZW52PXJmYzE5Il0sICJzZXJ2aWNlcyI6IFsiZGlkOnNvdjpXRmtRdW1XejlvazZVWEVLUDQ5NlVBIl19"))

"""