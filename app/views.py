from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from app.models import SubParser
from pymongo import MongoClient
from bson import ObjectId
import pymongo
import _thread


# Called by the url dispatcher when a user requests our site
# return - a rendered(if context is given) template object
def index(request):
    template = loader.get_template("app/index.html")
    return HttpResponse(template.render())


# Handles the first GET request made after the webapp is loaded in order to fetch essential data
# return - recent, favorites, and random subreddit results are automatically sent in the form of an object
def setup_data(request):
    recent_decoded = list()

    print("IN SETUP_DATA")
    parser = SubParser(0, 0)
    favorites = ["Oculus", "SpaceX", "Space", "Nasa", "VirtualReality", "WebDev", "GoLang"]
    recent = parser.connection.lrange("recent", 0, -1)

    for item in recent:
        recent_decoded.append(item.decode("utf-8"))
    print(recent_decoded)
    random = recent_decoded[:]
    random.extend(favorites)
    return JsonResponse({"recent": recent_decoded, "favorites": favorites, "random": random})


# Handles our main POST and GET requests
# POST request - Checks against the database for previous requests pertaining to the subreddit inputted by the user
# If no results are found then we search for related subreddits, otherwise we fetch the appropriate results from the database
# GET request - Checks against the memcache database to see the progress being made of our POST request
# request - an object that contains information about the request being made
# return - GET request will return either a number telling the user how far along the POST request is
# or if the POST request finishes, results in the form of an object containing related subreddit information
@csrf_exempt
def data(request):
    client = MongoClient()
    dbReddit_Link = client.Reddit_Link
    collection_requests = dbReddit_Link["requests"]
    collection_topsubs = dbReddit_Link["topsubs"]

    if request.method == "POST":
        print("SERVICING POST REQUEST")
        subreddit_name = request.POST["subreddit"].lower()
        search_type = request.POST["searchtype"]
        print(subreddit_name + " " + search_type)
        if search_type == "Fast":
            page_count = 1
        else:
            page_count = 5
        # If no POST request is already in progress for this subreddit then we can process it
        if collection_requests.find_one({"request": subreddit_name + "F"}) is None:
            collection_requests.insert_one({"request": subreddit_name + "F", "pdone": 0})
            parser = SubParser(subreddit_name, page_count)
            _thread.start_new_thread(parser.get_results, ())
        print("EXITING VIEWS.PY FROM POST REQUEST")
        return HttpResponse("OK")

    elif request.method == "GET":
        print("SERVICING GET REQUEST")
        subreddit_name = request.GET["subreddit"].lower()
        pdone = collection_requests.find_one({"request": subreddit_name + "F"})["pdone"]
        print("done: " + str(pdone))
        if pdone == 100:
            top_list = collection_topsubs.find_one({"subreddit": subreddit_name})["list"]
            return JsonResponse({"subreddits": top_list})
        print("EXITING VIEWS.PY FROM GET REQUEST")
        return HttpResponse(pdone)
    print("EXITING VIEWS.PY")