#!/bin/bash

# =============================================================================
# SSL Certificate Generation Script for BlogML Development
# =============================================================================
# This script generates self-signed SSL certificates for local development
# =============================================================================
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SSL_DIR="$(dirname "$0")/../nginx/ssl"
CERT_NAME="blogml"
DOMAIN="blogml.local"
ALT_DNS="localhost,127.0.0.1"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if OpenSSL is installed
check_dependencies() {
    if ! command -v openssl &> /dev/null; then
        print_error "OpenSSL is not installed. Please install OpenSSL first."
        exit 1
    fi
}

# Create SSL directory
create_ssl_directory() {
    print_status "Creating SSL directory at $SSL_DIR..."
    mkdir -p "$SSL_DIR"
    if [ ! -d "$SSL_DIR" ]; then
        print_error "Failed to create SSL directory."
        exit 1
    fi
}

# Generate SSL certificate
generate_certificate() {
    print_status "Generating SSL certificate for $DOMAIN..."

    # Create a configuration file for the certificate
    cat > "$SSL_DIR/openssl.conf" << EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C = US
ST = California
L = San Francisco
O = BlogML
OU = Development
CN = $DOMAIN

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DOMAIN
DNS.2 = localhost
DNS.3 = 127.0.0.1
IP.1 = 127.0.0.1
IP.2 = ::1
EOF

    # Generate private key
    print_status "Generating private key..."
    openssl genrsa -out "$SSL_DIR/key.pem" 2048

    # Generate certificate signing request
    print_status "Generating certificate signing request..."
    openssl req -new -key "$SSL_DIR/key.pem" -out "$SSL_DIR/cert.csr" -config "$SSL_DIR/openssl.conf"

    # Generate self-signed certificate
    print_status "Generating self-signed certificate..."
    openssl x509 -req -days 365 -in "$SSL_DIR/cert.csr" -signkey "$SSL_DIR/key.pem" -out "$SSL_DIR/cert.pem" -extensions v3_req -extfile "$SSL_DIR/openssl.conf"

    # Copy certificate to standard location
    cp "$SSL_DIR/cert.pem" "/etc/nginx/ssl/cert.pem" 2>/dev/null || true
    cp "$SSL_DIR/key.pem" "/etc/ssl/key.pem" 2>/dev/null || true

    # Clean up CSR file
    rm "$SSL_DIR/cert.csr"
}

# Verify certificate
verify_certificate() {
    print_status "Verifying generated certificate..."
    if openssl x509 -in "$SSL_DIR/cert.pem" -text -noout | grep -q "$DOMAIN"; then
        print_status "Certificate verified successfully!"
    else
        print_error "Certificate verification failed!"
        exit 1
    fi
}

# Display certificate information
display_info() {
    print_status "SSL Certificate Generated Successfully!"
    echo
    echo "Certificate Details:"
    echo "  - Certificate: $SSL_DIR/cert.pem"
    echo "  - Private Key:  $SSL_DIR/key.pem"
    echo "  - Domain:       $DOMAIN"
    echo "  - Valid for:    365 days"
    echo
    print_warning "This is a self-signed certificate for development only!"
    print_warning "Your browser will show security warnings - this is normal."
    echo
    print_status "To trust this certificate on macOS:"
    echo "  1. Double-click the certificate: $SSL_DIR/cert.pem"
    echo "  2. Add it to 'System' keychain"
    echo "  3. Set 'Always Trust' for SSL"
    echo "  4. Enter your admin password when prompted"
    echo
    print_status "To trust this certificate on Ubuntu/Debian:"
    echo "  sudo cp $SSL_DIR/cert.pem /usr/local/share/ca-certificates/blogml.crt"
    echo "  sudo update-ca-certificates"
}

# Check if certificates already exist
check_existing() {
    if [ -f "$SSL_DIR/cert.pem" ] && [ -f "$SSL_DIR/key.pem" ]; then
        print_warning "SSL certificates already exist!"
        read -p "Do you want to regenerate them? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "Keeping existing certificates."
            exit 0
        fi
        print_status "Regenerating certificates..."
    fi
}

# Main execution
main() {
    echo "========================================"
    echo "BlogML SSL Certificate Generator"
    echo "========================================"
    echo

    check_dependencies
    check_existing
    create_ssl_directory
    generate_certificate
    verify_certificate
    display_info

    echo
    print_status "SSL certificate setup complete!"
}

# Run the script
main "$@"