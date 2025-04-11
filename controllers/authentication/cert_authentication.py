from cryptography import x509
from cryptography.hazmat.primitives.serialization import pkcs12, Encoding
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID
import os

def load_p12(p12_path, password=None):
    with open(p12_path, "rb") as f:
        p12_data = f.read()
    private_key, certificate, _ = pkcs12.load_key_and_certificates(
        p12_data,
        password.encode() if password else None
    )
    print("Certificate:", certificate)

    pem_cert = certificate.public_bytes(Encoding.PEM).decode("utf-8")
    return pem_cert, private_key 

def sign_challenge(private_key, challenge):
    print("Signing challenge:", challenge)
    return private_key.sign(
        challenge,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

def verify_signature(certificate, challenge, signature):
    print("\n🧪 Verifying signature...")
    
    if isinstance(challenge, bytes):
        print("🔹 Challenge (bytes):", challenge.hex())
    else:
        print("⚠️ Challenge is not bytes! Type:", type(challenge))
        
    print("🔹 Signature:", signature.hex())
    print("🔹 Using certificate with CN:", extract_cn(certificate))

    public_key = certificate.public_key()
    
    try:
        public_key.verify(
            signature,
            challenge,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        print("✅ Valid signature!\n")
        valid = True
        return valid, extract_cn(certificate)
    except Exception as e:
        print("❌ Signature verification failed!")
        print("🧵 Exception:", repr(e))
        valid = False
        return valid, None


def extract_cn(certificate):
    subject = certificate.subject
    cn = subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    return cn

def reconstruct_pem(cert_pem):
    certificate = x509.load_pem_x509_certificate(cert_pem.encode("utf-8"))

    return certificate

#private_key, certificate = load_from_p12(p12_path)
#print("Signed challenge:", sign_challenge(private_key, challenge))
#print("Is it valid?", verify_signature(certificate, challenge, sign_challenge(private_key, challenge)))