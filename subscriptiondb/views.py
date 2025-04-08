from django.contrib.auth import logout
from django.shortcuts import render, redirect
from .firebase import database_ref, search_subscription_in_firebase

# Create your views here.
def home(request):
    return render(request, 'home.html')

def subscriptions(request):
    return render(request, 'subscriptions.html')

# Function to add user to Firebase Realtime Database
def add_subscription_to_firebase(appname, renewaldate, responsible, division, subject):
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

        add_subscription_to_firebase(appname, renewaldate, responsible, division, subject)
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




