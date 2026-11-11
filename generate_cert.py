"""
Genera un certificado TLS autofirmado para correr la app en https:// dentro
de la red local (la camara del navegador requiere https:// o localhost, no
funciona en http:// plano sobre una IP de red local).

Uso: python generate_cert.py
Escribe certs/cert.pem y certs/key.pem (gitignored).
"""
import datetime
import ipaddress
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

LAN_IP = "10.77.52.245"
OUT_DIR = Path(__file__).resolve().parent / "certs"
OUT_DIR.mkdir(exist_ok=True)

key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, "items-cedi-dashboard.local"),
])

cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)
    .public_key(key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.datetime.utcnow())
    .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=825))
    .add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
            x509.IPAddress(ipaddress.ip_address(LAN_IP)),
        ]),
        critical=False,
    )
    .sign(key, hashes.SHA256())
)

(OUT_DIR / "key.pem").write_bytes(
    key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
)
(OUT_DIR / "cert.pem").write_bytes(cert.public_bytes(serialization.Encoding.PEM))

print(f"Listo! Certificado generado en {OUT_DIR} (valido para localhost y {LAN_IP})")
