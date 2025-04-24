from django.contrib.auth import logout
from django.shortcuts import render, redirect
from datetime import datetime
from .firebase import database_ref, search_subscription_in_firebase, search_user_in_firebase
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



