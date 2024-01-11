import datetime
import decimal
import json
import os
import time
import csv
import bcrypt
from definitions import DATABASE
import sqlalchemy as db

# from lib_utils.utils import MyException
# from app.sql_init import sql_engine


# TODO Change this to using .csv files

def hash_password(password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')


def check_password(password, hashed_password):
    print("password: "+str(password))
    print("hashed_password: "+str(hashed_password))
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def find_user_by_email(email):
    with open(os.path.join(DATABASE, 'credentials.csv'), 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['email'] == email:
                return row
    return None


def add_user_to_csv(user_id, email, hashed_password):
    with open(os.path.join(DATABASE, 'credentials.csv'), 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_id, email, hashed_password])




#
# def db_insertUser(json_obj):
#     try:
#         ts = time.time()
#         timestamp = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
#         date_created = date_modified = date_last_access = timestamp
#         conn = sql_engine.connect()
#         metadata = db.MetaData(bind=sql_engine)
#         table = db.Table("users", metadata, autoload=True)
#         query_verify = db.select(table.c.email).where(
#             table.c.email == json_obj["email"]
#         )
#         emails = conn.execute(query_verify).fetchall()
#         if len(emails) > 0:
#             print("Email address is already in use: ", json_obj["email"])
#             raise MyException(
#                 "This email address is already in use. Please use another one"
#             )
#         password = encryptPassword(json_obj["password"])
#         settings = {}
#         query = db.insert(table).values(
#             user_id=None,
#             first_name=json_obj["first_name"],
#             last_name=json_obj["last_name"],
#             email=json_obj["email"],
#             password=password,
#             birthday=json_obj["birthday"],
#             admin=json_obj["admin"],
#             role=json_obj["role"],
#             feedback=json_obj["feedback"],
#             settings=settings,
#             description=json_obj["description"],
#             date_created=date_created,
#             date_last_access=date_last_access,
#             date_modified=date_modified,
#         )
#         conn.execute(query)
#         batch_id = conn.execute("SELECT LAST_INSERT_ID() AS id").fetchone()
#         return batch_id["id"]
#
#     except Exception as e:
#         raise e
#
#
# def db_verifyUser(json_obj):
#     try:
#         if "email" not in json_obj:
#             raise MyException("Valid email address not provided")
#         if "password" not in json_obj:
#             raise MyException("Valid password not provided")
#         conn = sql_engine.connect()
#         metadata = db.MetaData(bind=sql_engine)
#         table = db.Table("users", metadata, autoload=True)
#         query_verify = db.select(
#             table.c.user_id,
#             table.c.password,
#         ).where(table.c.email == json_obj["email"])
#         emails = conn.execute(query_verify).fetchall()
#         if len(emails) == 0:
#             print("User does not exist: ", json_obj["email"])
#             raise MyException(
#                 "This email address is not registered as a Reef.io member"
#             )
#         for (
#                 user_id,
#                 password,
#         ) in emails:
#             if verifyPassword(json_obj["password"], password):
#                 ts = time.time()
#                 timestamp = datetime.datetime.fromtimestamp(ts).strftime(
#                     "%Y-%m-%d %H:%M:%S"
#                 )
#                 date_last_access = timestamp
#                 query = (
#                     db.update(table)
#                     .values(date_last_access=date_last_access)
#                     .where(table.c.user_id == user_id)
#                 )
#                 conn.execute(query)
#                 return db_getUser(user_id)
#         raise MyException("Invalid email/password combination")
#
#     except Exception as e:
#         raise e
