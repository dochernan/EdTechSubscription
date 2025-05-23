from django.contrib.auth import logout
from django.shortcuts import render, redirect
from datetime import datetime
from .firebase import database_ref, search_subscription_in_firebase, search_user_in_firebase, save_user_to_firebase
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, 'home.html')

@login_required(login_url='/')
def subscriptions(request):
    return render(request, 'subscriptions.html')

@login_required(login_url='/')
def users(request):
    return render(request, 'users.html')

@login_required(login_url='/')
def contact_us(request):
    return render(request, 'contact_us.html')

@login_required(login_url='/')
def thank_you(request):
    return render(request, 'thank_you.html')

def aiguidelines(request):
    return render(request, 'aiguidelines.html')

def responsibleuse(request):
    return render(request, 'responsibleuse.html')

def faq(request):
    return render(request, 'faq.html')
@login_required(login_url='/')
def apps(request):
    snapshot = database_ref.child("subscriptions").get()

    apps = []
    if snapshot:
        for key, data in snapshot.items():
            apps.append({
                "name": data.get("appname"),
                "division": data.get("division"),
                "subject_tags": data.get("subject", "N/A"),
                "link": data.get("link"),
                "logo_url": data.get("logo_url") or "/static/images/default-logo.png",  # fallback
            })

    return render(request, "apps.html", {"apps": apps})


@login_required(login_url='/')
def request(request):

    snapshot = database_ref.child('requests').get()

    # Prepare the list of request data
    requests_data = []

    if snapshot:
        for key, value in snapshot.items():
            # Ensure 'subjects' is always a list
            value['subjects'] = value.get('subjects', [])
            requests_data.append(value)

    context = {
        'requests': requests_data
    }

    return render(request, 'request.html', context)


import uuid
from firebase_admin import storage


def upload_to_firebase_storage(file_obj, filename_prefix="logos"):
    """
    Uploads a file-like object to Firebase Storage and returns its public URL.
    """
    # Generate a unique filename
    unique_filename = f"{filename_prefix}/{uuid.uuid4().hex}_{file_obj.name}"

    # Get the Firebase bucket
    bucket = storage.bucket()

    # Create a blob and upload the file
    blob = bucket.blob(unique_filename)
    blob.upload_from_file(file_obj, content_type=file_obj.content_type)

    # Make the file publicly accessible
    blob.make_public()

    return blob.public_url


# Function to add user to Firebase Realtime Database
def add_subscription_to_firebase(appname, renewaldate, responsible, division, subject, cost_per_unit, num_licenses, cost_quote, link, admin_dashboard, admin_accounts, admin_username, admin_password, account_contact, renewal_recipient, edtech_notes, logo_url):
    # Ensure division is stored as a list in Firebase
    if isinstance(division, str):
        division = [division]

    if isinstance(subject, str):
        subject = [subject]

    subscriptions_ref = database_ref.child('subscriptions').push({
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
        'admin_password': admin_password,
        'account_contact': account_contact,
        'renewal_recipient': renewal_recipient,
        'edtech_notes': edtech_notes,
        'logo_url': logo_url,

    })
    return subscriptions_ref


# Function to retrieve subscriptions from Firebase Realtime Database
def get_subscriptions_from_firebase():
    subscriptions_ref = database_ref.child('subscriptions')
    subscriptions = subscriptions_ref.get()
    return subscriptions

# Function to retrieve subscriptions from Firebase Realtime Database
def get_users_from_firebase():
    users_ref = database_ref.child('users')
    users = users_ref.get()
    return users

@login_required(login_url='/')
def add_subscription(request):
    if request.method == 'POST':
        appname = request.POST.get('appname')
        renewaldate = request.POST.get('renewaldate')
        responsible = request.POST.get('responsible')
        division = request.POST.getlist('division')  # <-- updated to support multiple tags
        subject_raw = request.POST.get('subject', '')
        subject = [s.strip() for s in subject_raw.split(',') if s.strip()]
        cost_per_unit = request.POST.get('cost_per_unit')
        num_licenses = request.POST.get('num_licenses')
        cost_quote = request.POST.get('cost_quote')
        link = request.POST.get('link')
        admin_dashboard = request.POST.get('admin_dashboard')
        admin_accounts = request.POST.get('admin_accounts')
        admin_username = request.POST.get('admin_username')
        admin_password = request.POST.get('admin_password')
        account_contact = request.POST.get('account_contact')
        renewal_recipient = request.POST.get('renewal_recipient')
        edtech_notes = request.POST.get('edtech_notes')

        logo = request.FILES.get("logo")
        logo_url = None

        if logo:
            # Save to Firebase Storage or handle as needed
            logo_url = upload_to_firebase_storage(logo)  # you define this method

        else:
            logo_url = None

        add_subscription_to_firebase(appname, renewaldate, responsible, division, subject, cost_per_unit, num_licenses, cost_quote, link, admin_dashboard, admin_accounts, admin_username, admin_password, account_contact, renewal_recipient, edtech_notes, logo_url)
        return redirect('subscriptions')  # Redirect to the list_subscriptions view
    return render(request, 'add_subscription.html')

@login_required(login_url='/')
def list_subscriptions(request):
    search_query = request.GET.get("search", "").strip()

    if search_query:
        subscriptions = search_subscription_in_firebase("appname", search_query) or search_subscription_in_firebase("subject", search_query)
    else:
        subscriptions = get_subscriptions_from_firebase()

    return render(request, "subscriptions.html", {"subscriptions": subscriptions})

@login_required(login_url='/')
def list_users(request):
    search_query = request.GET.get("search", "").strip()
    users = {}

    if search_query:
        # Merge search results from both last_name and first_name
        last_name_matches = search_user_in_firebase("last_name", search_query) or {}
        first_name_matches = search_user_in_firebase("first_name", search_query) or {}

        users.update(last_name_matches)
        users.update(first_name_matches)
    else:
        users = get_users_from_firebase()

    # This must always be called
    return render(request, "users.html", {"users": users or {}})


def logout_view(request):
    logout(request)
    return redirect('/')
@login_required(login_url='/')
def delete_subscription(request, key):
    try:
        database_ref.child('subscriptions').child(key).delete()
    except Exception as e:
        print(f"Error deleting subscription: {e}")
    return redirect('subscriptions')  # Or wherever your list page is
@login_required(login_url='/')
def delete_user(request, key):
    try:
        database_ref.child('users').child(key).delete()
    except Exception as e:
        print(f"Error deleting user: {e}")
    return redirect('users')  # Or wherever your list page is

@login_required(login_url='/')
def edit_subscription(request, key):
    subscription_ref = database_ref.child('subscriptions').child(key)

    if request.method == 'POST':
        # Grab updated values from form and update Firebase
        updated_data = {
            'appname': request.POST.get('appname'),
            'renewaldate': request.POST.get('renewaldate'),
            'responsible': request.POST.get('responsible'),
            'division': request.POST.getlist('division'),
            'subject': [s.strip() for s in request.POST.get('subject', '').split(',') if s.strip()],
            'cost_per_unit': request.POST.get('cost_per_unit'),
            'num_licenses': request.POST.get('num_licenses'),
            'cost_quote': request.POST.get('cost_quote'),
            'link': request.POST.get('link'),
            'admin_dashboard': request.POST.get('admin_dashboard'),
            'admin_username': request.POST.get('admin_username'),
            'admin_password': request.POST.get('admin_password'),
            'account_contact': request.POST.get('account_contact'),
            'renewal_recipient': request.POST.get('renewal_recipient'),
            'edtech_notes': request.POST.get('edtech_notes')


            # Add other fields as needed...
        }
        subscription_ref.update(updated_data)
        return redirect('subscriptions')

    # GET request – display current values
    data = subscription_ref.get()
    context = {
        'key': key,
        'subscription': data,
        'division_tags': ['ES', 'MS', 'HS'],
    }
    return render(request, 'edit_subscription.html', context)
@login_required(login_url='/')
def edit_user(request, key):
    user_ref = database_ref.child('users').child(key)

    if request.method == 'POST':
        # Grab updated values from form and update Firebase
        updated_data = {
            'email': request.POST.get('email'),
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'username': request.POST.get('username'),
            'user_level': request.POST.get('user_level'),


        }
        user_ref.update(updated_data)
        return redirect('users')

    # GET request – display current values
    data = user_ref.get()
    context = {
        'key': key,
        'users': data,
    }
    return render(request, 'edit_user.html', context)



@login_required(login_url='/')
def contact_us(request):
    if request.method == 'POST':
        name = request.user.get_full_name()
        email = request.user.email
        requested_app = request.POST.get('requested_app')
        purpose = request.POST.get('purpose')
        link = request.POST.get('link')
        license_type = request.POST.get('license_type')
        subjects = request.POST.get('subjects')
        license_count = request.POST.get('license_count')
        cost_per_license = request.POST.get('cost_per_license')

        # Save the request to Firebase or your DB here if needed...
        # Save the request to Firebase
        request_data = {
            'requestor_name': name,
            'requestor_email': email,
            'requested_app': requested_app,
            'purpose': purpose,
            'link': link,
            'license_type': license_type,
            'subjects': [s.strip() for s in subjects.split(',') if s.strip()],
            'license_count': license_count,
            'cost_per_license': cost_per_license,
            'date_requested': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Push to Firebase under the 'requests' collection
        database_ref.child('requests').push(request_data)

        # Compose the confirmation email
        subject = f"EdTech Request Submitted: {requested_app}"
        message = (
            f"Hello {name},\n\n"
            f"Your request for \"{requested_app}\" has been successfully submitted.\n\n"
            f"Summary:\n"
            f"Purpose: {purpose}\n"
            f"Link: {link}\n"
            f"License Type: {license_type}\n"
            f"Subjects: {subjects}\n"
            f"Number of Licenses: {license_count}\n"
            f"Cost per License: {cost_per_license}\n\n"
            f"Thank you,\n"
            f"EdTech @ ISM"
        )

        send_mail(subject, message, None, [email], fail_silently=False)

        return redirect('thank_you')  # Or wherever you want to redirect
    return render(request, 'contact_us.html')

from django.http import JsonResponse

def ajax_search_subscriptions(request):
    search_query = request.GET.get('q', '').lower()
    results = []

    snapshot = database_ref.child('subscriptions').get()
    if snapshot:
        for key, sub in snapshot.items():
            name = sub.get('appname', '').lower()
            subject = ', '.join(sub.get('subject', [])).lower()
            if search_query in name or search_query in subject:
                results.append({
                    'key': key,
                    'appname': sub.get('appname'),
                    'renewaldate': sub.get('renewaldate'),
                    'responsible': sub.get('responsible'),
                    'division': sub.get('division', []),
                    'subject': sub.get('subject', [])
                })

    return JsonResponse({'subscriptions': results})


from django.http import JsonResponse, HttpResponseServerError


from django.http import JsonResponse, HttpResponseServerError

@login_required
def ajax_search_users(request):
    try:
        search_query = request.GET.get('q', '').lower()
        results = []

        snapshot = database_ref.child('users').get()
        if isinstance(snapshot, list):
            for idx, user in enumerate(snapshot):
                if not isinstance(user, dict):
                    continue
                last_name = user.get('last_name', '').lower()
                first_name = user.get('first_name', '').lower()
                if search_query in last_name or search_query in first_name:
                    results.append({
                        'key': str(idx),
                        'email': user.get('email'),
                        'last_name': user.get('last_name'),
                        'first_name': user.get('first_name'),
                        'username': user.get('username'),
                        'user_level': user.get('user_level'),
                    })

        elif isinstance(snapshot, dict):
            for key, user in snapshot.items():
                last_name = user.get('last_name', '').lower()
                first_name = user.get('first_name', '').lower()
                if search_query in last_name or search_query in first_name:
                    results.append({
                        'key': key,
                        'email': user.get('email'),
                        'last_name': user.get('last_name'),
                        'first_name': user.get('first_name'),
                        'username': user.get('username'),
                        'user_level': user.get('user_level'),
                    })

        return JsonResponse({'users': results})

    except Exception as e:
        return HttpResponseServerError(f'Error fetching users: {str(e)}')



from django.http import JsonResponse
from django.shortcuts import render
from .firebase import database_ref

def user_sidebar(request):
    users_ref = database_ref.child('users')
    users = users_ref.get()

    user_list = []
    if isinstance(users, list):
        for index, user_data in enumerate(users):
            if user_data:
                user_list.append({
                    'id': str(index),
                    'name': user_data.get('first_name') or user_data.get('email'),
                    'email': user_data.get('email')
                })
    elif isinstance(users, dict):
        for key, user_data in users.items():
            user_list.append({
                'id': key,
                'name': user_data.get('first_name') or user_data.get('email'),
                'email': user_data.get('email')
            })

    selected_user_id = request.GET.get('selected_user')
    selected_user = None

    for user in user_list:
        if user['id'] == selected_user_id:
            selected_user = user
            break

    return render(request, 'user_sidebar.html', {
        'users': user_list,
        'selected_user': selected_user
    })


from django.shortcuts import render, redirect
from datetime import datetime
from .firebase import database_ref  # Adjust this to your Firebase setup

def gogochat(request, chatid):
    current_user_id =  '2'#request.session.get('user_id')
    #if not current_user_id:
    #    return redirect('gologin')

    # Handle sending a new message (POST request)
    if request.method == 'POST':
        message = request.POST.get('message')
        message_date = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Save the message under the chat node (with Firebase-generated message ID)
        database_ref.child('chat').child(chatid).push({
            'sid': current_user_id,
            'message': message,
            'datetime': message_date,
        })

        return redirect('gogochat', chatid=chatid)

    # Handle loading messages (GET request)
    chat_snapshot = database_ref.child('chat').child(chatid).get()
    messages = []

    if isinstance(chat_snapshot, dict):
        for msg_id, msg_data in chat_snapshot.items():
            # Skip participants and created_at metadata
            if msg_id not in ['participants', 'created_at'] and isinstance(msg_data, dict):
                messages.append({
                    'id': msg_id,
                    'sid': msg_data.get('sid'),
                    'message': msg_data.get('message'),
                    'datetime': msg_data.get('datetime'),
                })

    # Sort messages by datetime if needed (optional)
    # messages.sort(key=lambda x: x['datetime'])

    return render(request, 'gochat.html', {
        'chatid': chatid,
        'messages': messages
    })



def create_chat(request):
    current_user_id = request.session.get('user_id')

    #if not current_user_id:
    #    return redirect('/')

    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        if recipient_id:
            from datetime import datetime
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

            # Generate new chat ID (Firebase push generates a unique key)
            new_chat_ref = database_ref.child('chat').push({
                'participants': {
                    'user1': current_user_id,
                    'user2': recipient_id,
                },
                'created_at': created_at
            })

            # Get the generated chatid (key)
            chatid = new_chat_ref.key

            # Redirect to the chat page for this conversation
            return redirect('gogochat', chatid=chatid)

    # If no recipient is selected or not POST
    return redirect('/')  # Or wherever your homepage is

def conversation_list(request):
    current_user_id = '2'#request.session.get('user_id')
    if not current_user_id:
        return redirect('gologin')

    chat_snapshot = database_ref.child('chat').get()
    conversations = []

    if isinstance(chat_snapshot, dict):
        for chat_key, chat_data in chat_snapshot.items():
            participants = chat_data.get('participants', {})
            if current_user_id in participants.values():
                conversations.append({
                    'chatid': chat_key,
                    'participants': participants,
                    'created_at': chat_data.get('created_at')
                })

    return render(request, 'conversation_list.html', {
        'conversations': conversations
    })


from django.shortcuts import render, redirect
from firebase_admin import db  # Ensure you've initialized Firebase correctly


def add_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Reference to users node
        users_ref = db.reference('users')

        # Check if email already exists in any child node
        users = users_ref.get()
        email_exists = False

        if users:
            for user_id, user_data in users.items():
                if user_data.get('email') == email:
                    email_exists = True
                    break

        if not email_exists:
            save_user_to_firebase(email)
        else:
            # You may also set a message to inform the user that the email already exists
            return render(request, 'add_user.html', {'error': 'Email already exists.'})

        return redirect('home')

    return render(request, 'add_user.html')


# views.py

from django.shortcuts import render
from .models_mssql import ITResource
#
# def it_resources(request):
#     resources = ITResource.objects.using('mssql').all()
#     return render(request, 'it_resources.html', {'resources': resources})

# views.py
import requests
from collections import defaultdict
from django.core.cache import cache
from django.core.paginator import Paginator
from django.shortcuts import render
#
# API_URL = "https://api.ismanila.org/DestinyResource/Destiny/FetchResources"
# AUTH_HEADER = "Basic OGtWNXo4T0NTSUdTcDoxfFJuOCFUNTk8XiVISWBJcw=="
# PAGE_SIZE = 100
# CACHE_TIMEOUT = 60 * 10
#
# ITEM_STATUS_LABELS = {
#     0: ('Available', 'success'),
#     100: ('Checked Out', 'primary'),
#     104: ('Out for Repairs', 'warning'),
#     200: ('Lost', 'danger'),
#     205: ('Retired', 'secondary'),
# }



# def fetch_api_resources():
#     cached_data = cache.get("cached_it_resources")
#     if cached_data:
#         return cached_data
#
#     all_data = []
#     page = 1
#     while True:
#         try:
#             response = requests.get(
#                 f"{API_URL}?pageNumber={page}&pageSize=500",
#                 headers={
#                     "accept": "*/*",
#                     "Authorization": AUTH_HEADER,
#                 },
#                 timeout=10
#             )
#             response.raise_for_status()
#             page_data = response.json()
#
#             if not page_data:
#                 break
#
#             all_data.extend(page_data)
#             page += 1
#
#         except requests.exceptions.RequestException as e:
#             print(f"API error on page {page}: {e}")
#             break
#
#     cache.set("cached_it_resources", all_data, CACHE_TIMEOUT)
#     return all_data
#
# def it_resources(request):
#     all_resources = fetch_api_resources()
#     status_choices = [(k, v[0]) for k, v in ITEM_STATUS_LABELS.items()]
#     # Filter based on multiple selected statuses (from GET parameters like ?status=0&status=100)
#     selected_statuses = request.GET.getlist("status")
#     if selected_statuses:
#         selected_statuses = set(map(int, selected_statuses))
#         all_resources = [res for res in all_resources if res.get("CurrentItemStatus") in selected_statuses]
#
#     # Replace SiteName with status label for display purposes
#     for item in all_resources:
#         status_id = item.get("CurrentItemStatus", 0)
#         label, color = ITEM_STATUS_LABELS.get(status_id, ('Unknown', 'dark'))
#         item["StatusLabel"] = label
#         item["StatusColor"] = color
#
#     # Group resources by ResourceTypeName
#     grouped = defaultdict(list)
#     for item in all_resources:
#         grouped[item.get("ResourceTypeName", "Unknown")].append(item)
#
#     # Convert dict to sorted list of tuples
#     grouped_resources = sorted(grouped.items())
#
#     # Paginate group list, not individual resources
#     paginator = Paginator(grouped_resources, PAGE_SIZE)
#     page_number = request.GET.get("page", 1)
#     page_obj = paginator.get_page(page_number)
#
#     return render(request, "it_resources.html", {
#         "grouped_resources": page_obj,
#         "selected_statuses": list(selected_statuses) if selected_statuses else [],
#         "status_choices": status_choices
#     })

# views.py
import requests
from collections import defaultdict
from django.core.cache import cache
from django.core.paginator import Paginator
from django.shortcuts import render

API_URL = "https://api.ismanila.org/DestinyResource/Destiny/FetchResources"
AUTH_HEADER = "Basic OGtWNXo4T0NTSUdTcDoxfFJuOCFUNTk8XiVISWBJcw=="
PAGE_SIZE = 100
CACHE_TIMEOUT = 60 * 10

ITEM_STATUS_LABELS = {
    0: ('Available', 'success'),
    100: ('Checked Out', 'primary'),
    104: ('Out for Repairs', 'warning'),
    200: ('Lost', 'danger'),
    205: ('Retired', 'secondary'),
    201: ('Stolen', 'warning'),
    202: ('No Longer in Use', 'warning'),
    204: ('Approved for Disposal' , 'warning'),
    206: ('Ready for Disposal' , 'warning')

}

def fetch_api_resources():
    cached_data = cache.get("cached_it_resources")
    if cached_data:
        return cached_data, False

    all_data = []
    page = 1
    while True:
        try:
            response = requests.get(
                f"{API_URL}?pageNumber={page}&pageSize=500",
                headers={
                    "accept": "*/*",
                    "Authorization": AUTH_HEADER,
                },
                timeout=10
            )
            response.raise_for_status()
            page_data = response.json()

            if not page_data:
                break

            all_data.extend(page_data)
            page += 1

        except requests.exceptions.RequestException as e:
            print(f"API error on page {page}: {e}")
            break

    cache.set("cached_it_resources", all_data, CACHE_TIMEOUT)
    return all_data, True

def it_resources(request):
    all_resources, loading = fetch_api_resources()

    selected_statuses = request.GET.getlist("status")
    if selected_statuses:
        selected_statuses = set(map(int, selected_statuses))
        all_resources = [res for res in all_resources if res.get("CurrentItemStatus") in selected_statuses]

    for item in all_resources:
        status_id = item.get("CurrentItemStatus", 0)
        label, color = ITEM_STATUS_LABELS.get(status_id, ('Unknown', 'dark'))
        item["StatusLabel"] = label
        item["StatusColor"] = color

    grouped = defaultdict(list)
    for item in all_resources:
        grouped[item.get("ResourceTypeName", "Unknown")].append(item)

    grouped_resources = sorted(grouped.items())

    paginator = Paginator(grouped_resources, PAGE_SIZE)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    status_choices = [(k, v[0]) for k, v in ITEM_STATUS_LABELS.items()]

    return render(request, "it_resources.html", {
        "grouped_resources": page_obj,
        "selected_statuses": list(selected_statuses) if selected_statuses else [],
        "status_choices": status_choices,
        "loading": loading
    })
