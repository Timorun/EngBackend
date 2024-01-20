import base64
import datetime
import decimal
import json
import os
import time
import csv
import bcrypt
from definitions import DATABASE


def hash_password(password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')


def check_password(password, hashed_password):
    # print("password: " + str(password))
    # print("hashed_password: " + str(hashed_password))
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def find_user_by_email(cipher_suite, email):
    with open(os.path.join(DATABASE, 'credentials.csv'), 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # print(cipher_suite)
            decrypted_row = [cipher_suite.decrypt(base64.urlsafe_b64decode(column)).decode() for column in row.values()]
            # print(decrypted_row)
            if decrypted_row[1] == email:  # Assuming email is the second column
                return {
                    'user_id': decrypted_row[0],
                    'email': decrypted_row[1],
                    'hashed_password': decrypted_row[2]
                }
    return None


def add_user_to_csv(cipher_suite, user_id, email, hashed_password):
    encrypted_row = [base64.urlsafe_b64encode(cipher_suite.encrypt(str(column).encode())).decode() for column in [user_id, email, hashed_password]]
    with open(os.path.join(DATABASE, 'credentials.csv'), 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(encrypted_row)


# Check if JWT user has is allowed to access module and presentation
def accesscheck(cipher_suite, userid, modulecode, presentationcode):
    try:
        with open(os.path.join(DATABASE, 'courseaccess.csv'), 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                encrypted_row = row[0]
                decrypted_row_str = cipher_suite.decrypt(base64.urlsafe_b64decode(encrypted_row)).decode()
                decrypted_row = decrypted_row_str.split(',')
                if (decrypted_row[0] == userid and
                        decrypted_row[1] == modulecode and
                        decrypted_row[2] == presentationcode):
                    # Append a tuple of (module_code, presentation_code) to the courses list
                    return True
    except IOError:
        return False
    return False
