import firebase_admin
from firebase_admin import credentials, db
import os

# Path to the serviceAccountKey.json file
cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH")
current_directory = os.path.dirname(os.path.abspath(__file__))

# Initialize the Firebase Admin SDK
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://edtech-e32be-default-rtdb.asia-southeast1.firebasedatabase.app/'  # Replace with your Firebase database URL
})

# Reference to the Realtime Database
database_ref = db.reference()

# Function to add a user to Firebase
def add_subscription_to_firebase(appname, renewaldate, responsible, division, subject, cost_per_unit, num_licenses, cost_quote, link, admin_dashboard, admin_accounts, admin_username, admin_password, account_contact, renewal_recipient, edtech_notes):
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

    })
    return app_ref


def get_subscriptions_from_firebase():
    subscriptions_ref = database_ref.child('subscriptions')
    subscriptions = subscriptions_ref.get()  # Fetch all subscriptions from the database
    return subscriptions

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


