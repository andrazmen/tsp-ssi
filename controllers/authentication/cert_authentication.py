from cryptography import x509
from cryptography.x509 import load_pem_x509_certificate, load_der_x509_certificate
from cryptography.hazmat.primitives.serialization import pkcs12, Encoding
from cryptography.hazmat.primitives.asymmetric import padding, rsa, ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
#from certvalidator import CertificateValidator, ValidationContext
#from oscrypto import asymmetric
import os
from datetime import datetime

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
    print("\nVerifying signature...")
    
    if isinstance(challenge, bytes):
        print("Challenge (bytes):", challenge.hex())
    else:
        print("Challenge is not bytes! Type:", type(challenge))
        
    print("Signature:", signature.hex())
    print("Using certificate with CN:", extract_cn(certificate))

    public_key = certificate.public_key()
    
    try:
        public_key.verify(
            signature,
            challenge,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        print("Valid signature!\n")
        valid = True
        return valid, extract_cn(certificate)
    except Exception as e:
        print("Signature verification failed!")
        print("Exception:", repr(e))
        valid = False
        return valid, None


def extract_cn(certificate):
    subject = certificate.subject
    cn = subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    return cn

def reconstruct_pem(cert_pem):
    try:    
        certificate = x509.load_pem_x509_certificate(cert_pem.encode("utf-8"))
    except Exception as e:
        print("Reconstructing pem failed:", e)
        return False
    return certificate

def validate_certificate_chain(cert):
    try:
        root = load_pem_x509_certificate(open("/home/andraz/tsp/CA-si/root-ca_rsa.pem", "rb").read(), default_backend())
        issuing_ca  = load_pem_x509_certificate(open("/home/andraz/tsp/CA-si/issuing-ca_rsa.pem", "rb").read(), default_backend())

        chain = [cert] + [issuing_ca]
        trusted_roots = [root]

        # Verify certificate in the chain
        issuer_cert = chain[1]
        subject_cert = chain[0]

        if subject_cert.issuer != issuer_cert.subject:
            raise Exception("Issuer subject mismatch in chain")

        # Get public key
        public_key = issuer_cert.public_key()

        # Determine padding (simplified for RSA)
        if isinstance(public_key, rsa.RSAPublicKey):
            pad = padding.PKCS1v15()
        elif isinstance(public_key, ec.EllipticCurvePublicKey):
            pad = None  # EC doesn't use padding
        else:
            raise Exception("Unsupported key type")

        public_key.verify(
            subject_cert.signature,
            subject_cert.tbs_certificate_bytes,
            pad,
            subject_cert.signature_hash_algorithm,
        )

        # Validate root
        if issuer_cert.issuer == root.subject:
            root.public_key().verify(
                issuer_cert.signature,
                issuer_cert.tbs_certificate_bytes,
                padding.PKCS1v15() if isinstance(root.public_key(), rsa.RSAPublicKey) else None, 
                issuer_cert.signature_hash_algorithm,
            )
        else:
            raise Exception("Root did not match issuer of issuing ca")

        # Date validity check
        now = datetime.utcnow()
        for c in chain + trusted_roots:
            if not (c.not_valid_before <= now <= c.not_valid_after):
                raise Exception(f"Certificate expired or not yet valid: {c.subject}")
        return True

    except Exception as e:
        print("Certificate chain validation failed:", e)
        return False

