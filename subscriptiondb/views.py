from django.contrib.auth import logout
from django.shortcuts import render, redirect
from .firebase import database_ref, search_subscription_in_firebase

# Create your views here.
def home(request):
    return render(request, 'home.html')

def subscriptions(request):
    return render(request, 'subscriptions.html')

# Function to add user to Firebase Realtime Database
def add_subscription_to_firebase(appname, renewaldate, responsible, division, subject, cost_per_unit, num_licenses, cost_quote, link, admin_dashboard, admin_accounts, admin_username, admin_password, account_contact, renewal_recipient, edtech_notes):
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
        'edtech_notes': edtech_notes

    })
    return subscriptions_ref


# Function to retrieve subscriptions from Firebase Realtime Database
def get_subscriptions_from_firebase():
    subscriptions_ref = database_ref.child('subscriptions')
    subscriptions = subscriptions_ref.get()
    return subscriptions

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
        admin_username = request.POST.get('admin_username')
        admin_password = request.POST.get('admin_password')
        account_contact = request.POST.get('account_contact')
        renewal_recipient = request.POST.get('renewal_recipient')
        edtech_notes = request.POST.get('edtech_notes')

        add_subscription_to_firebase(appname, renewaldate, responsible, division, subject, cost_per_unit, num_licenses, cost_quote, link, admin_dashboard, admin_username, admin_password, account_contact, renewal_recipient, edtech_notes)
        return redirect('subscriptions')  # Redirect to the list_subscriptions view
    return render(request, 'add_subscription.html')


def list_subscriptions(request):
    search_query = request.GET.get("search", "").strip()

    if search_query:
        subscriptions = search_subscription_in_firebase("appname", search_query) or search_subscription_in_firebase("subject", search_query)
    else:
        subscriptions = get_subscriptions_from_firebase()

    return render(request, "subscriptions.html", {"subscriptions": subscriptions})

def logout_view(request):
    logout(request)
    return redirect('/')

def delete_subscription(request, key):
    try:
        database_ref.child('subscriptions').child(key).delete()
    except Exception as e:
        print(f"Error deleting subscription: {e}")
    return redirect('subscriptions')  # Or wherever your list page is


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




