import firebase_admin
from firebase_admin import credentials, db
import os
import base64
import json

from firebase_admin import credentials, initialize_app


#
#
# # Path to the serviceAccountKey.json file
# cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH")
# current_directory = os.path.dirname(os.path.abspath(__file__))
#
#
#
# # Initialize the Firebase Admin SDK
# cred = credentials.Certificate(cred_path)
# firebase_admin.initialize_app(cred, {
#    'databaseURL': 'https://edtech-e32be-default-rtdb.asia-southeast1.firebasedatabase.app/'  # Replace with your Firebase database URL
# })
#
# # Reference to the Realtime Database
# database_ref = db.reference()
import os
import json
import firebase_admin
from firebase_admin import credentials, db

def get_firebase_credentials():
    # Try loading from file path (local dev)
    cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH")
    if cred_path and os.path.exists(cred_path):
        return credentials.Certificate(cred_path)

    # Else, try from string (Vercel env var)
    firebase_creds_str = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    if firebase_creds_str:
        firebase_creds_dict = json.loads(firebase_creds_str)
        return credentials.Certificate(firebase_creds_dict)

    raise ValueError("Firebase credentials not found.")



# Initialize only if not already initialized
if not firebase_admin._apps:
    cred = get_firebase_credentials()
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://edtech-e32be-default-rtdb.asia-southeast1.firebasedatabase.app/',
        'storageBucket': 'edtech-e32be.firebasestorage.app'

    })

database_ref = db.reference()



# Function to add a user to Firebase
def add_subscription_to_firebase(appname, renewaldate, responsible, division, subject, cost_per_unit, num_licenses, cost_quote, link, admin_dashboard, admin_accounts, admin_username, admin_password, account_contact, renewal_recipient, edtech_notes, logo_url):
    # Ensure division is stored as a list in Firebase
    if isinstance(division, str):
        division = [division]  # fallback in case it's passed as a single string

    if isinstance(subject, str):
        subject = [subject]

    app_ref = database_ref.child('subscriptions').push({
        'appname': appname,
        'renewaldate': renewaldate,
        'responsible': responsible,
        'division': division,
        'subject': subject,
        'cost_per_unit': cost_per_unit,
        'num_licenses': num_licenses,
        'cost_quote': cost_quote,
        'link': link,
        'admin_dashboard': admin_dashboard,
        'admin_accounts': admin_accounts,
        'admin_username': admin_username,
        'admin_password' : admin_password,
        'account_contact': account_contact,
        'renewal_recipient': renewal_recipient,
        'edtech_notes': edtech_notes,
        'logo_url': logo_url,

    })
    return app_ref



# def get_subscriptions_from_firebase():
#     subscriptions_ref = database_ref.child('subscriptions')
#     subscriptions = subscriptions_ref.get()  # Fetch all subscriptions from the database
#     return subscriptions

from google.cloud import storage

def get_subscriptions_from_firebase():
    subscriptions_ref = database_ref.child('subscriptions')
    subscriptions = subscriptions_ref.get()  # Dict of all subscriptions
    updated_subscriptions = {}

    # Initialize Firebase Storage client
    storage_client = storage.Client()
    bucket = storage_client.bucket("edtech-e32be.firebasestorage.app")

    if subscriptions:
        for key, data in subscriptions.items():
            logo_path = data.get('logo_path')  # e.g., 'uploads/logos/canva.png'

            if logo_path:
                blob = bucket.blob(logo_path)
                try:
                    # Generate a signed URL valid for 1 hour (3600 seconds)
                    url = blob.generate_signed_url(version="v4", expiration=3600)
                    data['logo_url'] = url
                except Exception as e:
                    print(f"Error generating URL for {logo_path}: {e}")
                    data['logo_url'] = None
            else:
                data['logo_url'] = None

            updated_subscriptions[key] = data

    return updated_subscriptions

def get_users_from_firebase():
    users_ref = database_ref.child('users')
    raw_data = users_ref.get()  # Fetch all users from the database

    normalized_users = {}

    if isinstance(raw_data, dict):
        # Already in desired format
        return raw_data

    elif isinstance(raw_data, list):
        # Convert list to dict using index or UID if available
        for index, user in enumerate(raw_data):
            if isinstance(user, dict):
                key = user.get('uid') or f"user_{index}"
                normalized_users[key] = user

        return normalized_users

    return {}  # Return empty dict if no users or unexpected format


def search_subscription_in_firebase(search_key, search_value):
    subscriptions = get_subscriptions_from_firebase()

    if subscriptions:
        for subscription_id, subscription_data in subscriptions.items():
            if subscription_data.get(search_key) == search_value:
                return {subscription_id: subscription_data}  # Return subscription details if found

    return None  # Return None if subscription is not found

# def search_user_in_firebase(search_key, search_value):
#     users = get_users_from_firebase()
#
#     if users:
#         for user_id, user_data in users.items():
#             if user_data.get(search_key) == search_value:
#                 return {user_id: user_data}  # Return subscription details if found
#
#     return None  # Return None if subscription is not found

def search_user_in_firebase(search_key, search_value):
    users = get_users_from_firebase()
    results = {}

    if users:
        search_value = search_value.lower().strip()

        for user_id, user_data in users.items():
            field_value = str(user_data.get(search_key, "")).lower()

            if search_value in field_value:
                results[user_id] = user_data

    return results if results else None


def save_user_to_firebase(user):
    user_ref = database_ref.child('users').child(str(user.id))

    # Check if user already exists in Firebase
    if user_ref.get() is None:
        user_ref.set({
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_level': 'Basic',
        })


