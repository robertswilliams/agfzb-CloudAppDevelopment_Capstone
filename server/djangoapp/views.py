from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarMake, CarModel
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import uuid

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://50e8cf6a.us-south.apigw.appdomain.cloud/api/dealership/dealer-get"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context['dealership_list'] = dealerships

        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context = {}
        url = "https://50e8cf6a.us-south.apigw.appdomain.cloud/api/review/review-get"
        # Get reviews from the URL
        reviews = get_dealer_reviews_from_cf(url, dealerId=dealer_id)
        context['review_list'] = reviews
        context['dealer_id'] = dealer_id

        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {}
    if request.method == "POST":
        url = "https://50e8cf6a.us-south.apigw.appdomain.cloud/api/review/review-post"
        review = {}
        # I need to redo this, since it doesn't
        # reflect what's actually in request.POST.
        # See notes.

        print('add_review (POST): ')
        print(request.POST)
        print('')

        # I need a username
        username = request.POST['username']
        user = User.objects.get(username=username)

        review_time = datetime.utcnow().isoformat()
        review_content = request.POST['content']
        id = uuid.uuid4()
        name = username
        if user.first_name:
            lastname = ' ' + user.last_name if user.last_name else ''
            name = user.first_name + lastname            
        purchased = 'purchasecheck' in request.POST
        date_purchased = None
        car_make = None
        car_model = None
        car_year = None
        if purchased:
            date_purchased = request.POST['purchasedate']

            print('car index: ', request.POST['car'])

            cars = CarModel.objects.all()
            # I'm not sure why but all car models
            # are offset by 2 from the first model
            # in the list
            base = 2 
            print('cars: ', cars)
            car = cars[int(request.POST['car']) - base]
            car_make = car.make
            car_model = car.name
            car_year = car.year.strftime("%Y")

        print('time: ', review_time)
        print('dealership: ', dealer_id)
        print('review: ', review_content)
        print('make: ', car_make)
        print('model: ', car_model)
        print('year: ', car_year)
        print('id: ', id)
        print('name: ', name)
        print('purchased: ', purchased)
        print('purchase_date: ', date_purchased)

        review["time"] = review_time
        review["dealership"] = dealer_id
        review["review"] = review_content
        review["car_make"] = car_make
        review["car_model"] = car_model
        review["car_year"] = car_year
        review["id"] = id
        review["name"] = name
        review["purchase"] = purchased
        review["purchase_date"] = date_purchased
        
        ########################################
        # Hacked breakpoint so that I don't try
        # to post a review before I'm ready
        print('BREAKPOINT')
        breakpoint = []
        print(breakpoint[1])
        print('should not reach this!')
        ########################################

        json_payload = {"review" : review}

        #result = post_request(url, json_payload, dealerId=dealer_id)

        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
    elif request.method == "GET":
        url = "https://50e8cf6a.us-south.apigw.appdomain.cloud/api/dealership/dealer-get"
        dealer_name = "Unknown"
        dealerships = get_dealers_from_cf(url)
        for dealer in dealerships:
            if dealer.id == dealer_id:
                dealer_name = dealer.full_name
                break
        context['cars'] = CarModel.objects.filter(dealerId=dealer_id)
        context['dealer_id'] = dealer_id
        context['dealer_name'] = dealer_name
        return render(request, 'djangoapp/add_review.html', context)
