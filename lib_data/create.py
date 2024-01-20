import base64
import csv
import os

from lib_data.database import hash_password
from definitions import DATABASE

## Initialize encrypted credentials.csv and access.csv, for prototype

# Create encrypted credentials table
def createcredentials(cipher_suite):

    headers = ["user_id", "email", "hashed_password"]
    rows = [
        [1, "user1@example.com", hash_password("pw1")],
        [2, "user2@example.com", hash_password("pw2")]
    ]

    credentials_path = os.path.join(DATABASE, 'credentials.csv')
    with open(credentials_path, 'w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow(headers)

        for row in rows:
            # Encrypt each column in the row and encode it in Base64
            encrypted_row = [base64.urlsafe_b64encode(cipher_suite.encrypt(str(column).encode())).decode() for column in
                             row]
            writer.writerow(encrypted_row)


# Create encrypted course access table
def createaccess(cipher_suite):

    headers = ['user_id', 'module_code', 'presentation_code']
    rows = [
        [1, "BBB", "2014J"],
        [1, "FFF", "2014J"],
        [2, "FFF", "2014J"],
        [2, "BBB", "2014J"],
    ]

    access_path = os.path.join(DATABASE, 'courseaccess.csv')
    with open(access_path, 'w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow(headers)

        for row in rows:
            row_str = ','.join(map(str, row))
            encrypted_row = base64.urlsafe_b64encode(cipher_suite.encrypt(row_str.encode())).decode()
            writer.writerow([encrypted_row])
