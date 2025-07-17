#!/usr/bin/env python3
"""
File encryption/decryption utility.

Usage:
    python file_crypto.py <filepath> <password> [-e|-d]

Examples:
    python file_crypto.py document.txt mypassword -e    # Encrypt document.txt to document.txt.locked
    python file_crypto.py document.txt.locked mypassword -d  # Decrypt document.txt.locked to document.txt
"""

import argparse
import os
import sys
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


def derive_key_from_password(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """Derive a key from password using PBKDF2."""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt


def encrypt_file(filepath: str, password: str) -> None:
    """Encrypt a file and save it with .locked suffix."""
    input_path = Path(filepath)
    
    if not input_path.exists():
        print(f"Error: File '{filepath}' does not exist.")
        sys.exit(1)
    
    if input_path.suffix == '.locked':
        print(f"Error: File '{filepath}' is already encrypted (.locked suffix).")
        sys.exit(1)
    
    # Read the original file
    try:
        with open(input_path, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"Error reading file '{filepath}': {e}")
        sys.exit(1)
    
    # Derive key from password
    key, salt = derive_key_from_password(password)
    fernet = Fernet(key)
    
    # Encrypt the data
    encrypted_data = fernet.encrypt(data)
    
    # Create output filename with .locked suffix
    output_path = input_path.with_suffix(input_path.suffix + '.locked')
    
    # Write encrypted data with salt prepended
    try:
        with open(output_path, 'wb') as f:
            f.write(salt + encrypted_data)
        print(f"File encrypted successfully: {output_path}")
    except Exception as e:
        print(f"Error writing encrypted file: {e}")
        sys.exit(1)


def decrypt_file(filepath: str, password: str) -> None:
    """Decrypt a file and save it without .locked suffix."""
    input_path = Path(filepath)
    
    if not input_path.exists():
        print(f"Error: File '{filepath}' does not exist.")
        sys.exit(1)
    
    if not input_path.suffix == '.locked':
        print(f"Error: File '{filepath}' does not have .locked suffix.")
        sys.exit(1)
    
    # Read the encrypted file
    try:
        with open(input_path, 'rb') as f:
            encrypted_data_with_salt = f.read()
    except Exception as e:
        print(f"Error reading file '{filepath}': {e}")
        sys.exit(1)
    
    if len(encrypted_data_with_salt) < 16:
        print("Error: File appears to be corrupted or not encrypted.")
        sys.exit(1)
    
    # Extract salt and encrypted data
    salt = encrypted_data_with_salt[:16]
    encrypted_data = encrypted_data_with_salt[16:]
    
    # Derive key from password
    try:
        key, _ = derive_key_from_password(password, salt)
        fernet = Fernet(key)
        
        # Decrypt the data
        decrypted_data = fernet.decrypt(encrypted_data)
    except Exception as e:
        print(f"Error: Failed to decrypt file. Incorrect password or corrupted file.")
        sys.exit(1)
    
    # Create output filename without .locked suffix
    output_path = input_path.with_suffix('')
    
    # Write decrypted data
    try:
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
        print(f"File decrypted successfully: {output_path}")
    except Exception as e:
        print(f"Error writing decrypted file: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Encrypt or decrypt files using password-based encryption.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.txt mypassword -e    # Encrypt document.txt to document.txt.locked
  %(prog)s document.txt.locked mypassword -d  # Decrypt document.txt.locked to document.txt
        """
    )
    
    parser.add_argument('filepath', help='Path to the file to encrypt or decrypt')
    parser.add_argument('password', help='Password for encryption/decryption')
    parser.add_argument('-e', '--encrypt', action='store_true', help='Encrypt the file')
    parser.add_argument('-d', '--decrypt', action='store_true', help='Decrypt the file')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.encrypt and args.decrypt:
        print("Error: Cannot specify both -e and -d flags.")
        sys.exit(1)
    
    if not args.encrypt and not args.decrypt:
        print("Error: Must specify either -e (encrypt) or -d (decrypt) flag.")
        sys.exit(1)
    
    # Determine operation based on file extension and flags
    filepath = args.filepath
    password = args.password
    
    if args.encrypt:
        encrypt_file(filepath, password)
    elif args.decrypt:
        decrypt_file(filepath, password)


if __name__ == '__main__':
    main() 