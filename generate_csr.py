from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
import datetime
import os

def generate_csr_and_key():
    """Generate a private key and CSR for a domain."""
    print("Generating CSR (Certificate Signing Request) for DorkySearch.com")
    print("=================================================================")
    
    # Get domain information
    domain = input("Domain name [DorkySearch.com]: ") or "DorkySearch.com"
    country = input("Country Name (2 letter code) [US]: ") or "US"
    state = input("State or Province Name [California]: ") or "California"
    locality = input("Locality Name (city) [San Francisco]: ") or "San Francisco"
    organization = input("Organization Name [DorkySearch Inc]: ") or "DorkySearch Inc"
    org_unit = input("Organizational Unit Name [IT]: ") or "IT"
    email = input("Email Address [admin@dorkysearch.com]: ") or "admin@dorkysearch.com"
    
    # Generate a private key
    print("\nGenerating private key...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Write the private key to a file
    with open(f"{domain.replace('.', '_')}_private.key", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Generate a CSR
    print("Generating CSR...")
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, country),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state),
        x509.NameAttribute(NameOID.LOCALITY_NAME, locality),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, org_unit),
        x509.NameAttribute(NameOID.COMMON_NAME, domain),
        x509.NameAttribute(NameOID.EMAIL_ADDRESS, email),
    ])).sign(private_key, hashes.SHA256())
    
    # Write the CSR to a file
    csr_filename = f"{domain.replace('.', '_')}.csr"
    with open(csr_filename, "wb") as f:
        f.write(csr.public_bytes(serialization.Encoding.PEM))
    
    # Also write the CSR content to a text file for easy copying
    with open(f"{domain.replace('.', '_')}_csr.txt", "w") as f:
        with open(csr_filename, "rb") as csr_file:
            f.write(csr_file.read().decode('utf-8'))
    
    print("\n=================================================================")
    print(f"Private key saved to: {domain.replace('.', '_')}_private.key")
    print(f"CSR saved to: {csr_filename}")
    print(f"CSR content also saved as text to: {domain.replace('.', '_')}_csr.txt")
    print("\nIMPORTANT: Keep your private key secure and never share it!")
    print("Use the content of the CSR file when ordering your SSL certificate.")
    
    # Display the CSR content
    print("\nCSR Content (copy this to your SSL provider):")
    print("=================================================================")
    with open(csr_filename, "rb") as f:
        print(f.read().decode('utf-8'))
    print("=================================================================")

if __name__ == "__main__":
    try:
        generate_csr_and_key()
    except Exception as e:
        print(f"Error generating CSR: {e}")
        print("\nYou may need to install the cryptography package:")
        print("pip install cryptography")
        
        # Try to install the package automatically
        try:
            import subprocess
            print("\nAttempting to install the required package...")
            subprocess.check_call(["pip", "install", "cryptography"])
            print("\nPackage installed. Please run this script again.")
        except Exception as install_error:
            print(f"Could not automatically install: {install_error}")
            print("Please install it manually with: pip install cryptography") 