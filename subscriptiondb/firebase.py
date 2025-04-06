import firebase_admin
from firebase_admin import credentials, db
import os



# Path to the serviceAccountKey.json file
current_directory = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_directory, 'edtech-e32be-firebase-adminsdk-fbsvc-e00807520f.json')

# Initialize the Firebase Admin SDK
cred = credentials.Certificate(json_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://edtech-e32be-default-rtdb.asia-southeast1.firebasedatabase.app/'  # Replace with your Firebase database URL
})

# Reference to the Realtime Database
database_ref = db.reference()

# Function to add a user to Firebase
def add_subscription_to_firebase(appname, renewaldate, responsible, division, subject):
    app_ref = database_ref.child('subscriptions').push({
        'appname': appname,
        'renewaldate': renewaldate,
        'responsible': responsible,
        'division': division,
        'subject': subject,
    })
    return app_ref

def get_subscriptions_from_firebase():
    subscriptions_ref = database_ref.child('subscriptions')
    subscriptions = subscriptions_ref.get()  # Fetch all subscriptions from the database
    return subscriptions


def search_subscription_in_firebase(search_key, search_value):
    subscriptions = get_subscriptions_from_firebase()

    if subscriptions:
        for subscription_id, subscription_data in subscriptions.items():
            if subscription_data.get(search_key) == search_value:
                return {subscription_id: subscription_data}  # Return subscription details if found

    return None  # Return None if subscription is not found