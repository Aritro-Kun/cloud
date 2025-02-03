from flask import Flask, request, render_template
from flask_cors import CORS
import mysql.connector as sqlcon
import os
from dotenv import load_dotenv
from datetime import datetime
import hashlib

app = Flask(__name__)
CORS(app)

load_dotenv(dotenv_path = "D:/chatspace/resources.env")

db_user = os.getenv("DB_user")
db_host = os.getenv("DB_host")
db_pass = os.getenv("DB_pass")
db_name = os.getenv("DB_name")

connection = sqlcon.connect(
    host = db_host,
    user = db_user,
    password = db_pass,
    database = db_name
)

def clear_expired_entries():
    if not connection.is_connected():
        connection.reconnect()
    current_time = datetime.now()
    clearing_expired_query = "DELETE FROM test_tempo_login WHERE token_expiry < %s"
    cursor = connection.cursor()
    cursor.execute(clearing_expired_query, (current_time,))
    connection.commit()
    cursor.close()

def clear_verified_entries():
    if not connection.is_connected():
        connection.reconnect()
    clearing_verified_query = "DELETE FROM test_tempo_login WHERE status = %s"
    cursor = connection.cursor()
    cursor.execute(clearing_verified_query, ('otp_received',))
    connection.commit()
    cursor.close()

@app.route("/verify_and_login")
def verify_mail_for_login():
    clear_expired_entries()
    clear_verified_entries()
    mailid = request.args.get('email')
    token = request.args.get('token')
    if not mailid or not token:
        return "Invalid Request", 400 #in future, try to create a html page, where you show this thingy. or maybe assign am open source contribution opton for some contributor.
    hashed_mail = hashlib.sha256(mailid.encode()).hexdigest()
    hashed_token = hashlib.sha256(token.encode()).hexdigest()
    if not connection.is_connected():
        connection.reconnect()
    cursor = connection.cursor()
    verifying_query = "SELECT * FROM test_tempo_login WHERE hashed_user_mail = %s AND token = %s AND token_expiry > %s"
    cursor.execute(verifying_query, (hashed_mail, hashed_token, datetime.now()))
    verifying_result = cursor.fetchone()
    if verifying_result is not None:
        update_query = "UPDATE test_tempo_login SET status = %s WHERE hashed_user_mail = %s"
        cursor.execute(update_query, ('otp_received', hashed_mail))
        connection.commit()
        cursor.close()
        return render_template("login_verification_success.html")
    else:
        cursor.close()
        return render_template("login_verification_failed.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug = True)
