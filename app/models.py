__author__ = 'Ben'
from app.captest import LimitTest
from app.subreddit import SubReddit
from pymongo import MongoClient
from pymongo import ReturnDocument
from bson import ObjectId
import datetime, pymongo, time, re, csv, requests, praw, redis


class SubParser:
    def __init__(self, subreddit_name, page_count):
        pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        self.connection = redis.StrictRedis(connection_pool=pool)

        if subreddit_name != 0:
            self.subreddit_name = subreddit_name
            self.page_count = page_count
            self.limit = LimitTest(0)
            client = MongoClient()
            dbreddit_link = client.Reddit_Link
            self.collection_posts = dbreddit_link[subreddit_name + "posts"]  # stores posts urls
            self.collection_subs = dbreddit_link[subreddit_name]  # stores html of user history page
            self.collection_requests = dbreddit_link["requests"]  # stores percent done of subreddit requested
            self.collection_topsubs = dbreddit_link["topsubs"]
            self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:42.0) Gecko/20100101 Firefox/42.0'}
            self.r = praw.Reddit(user_agent='my_cool_application by Frenchiie')


    def get_results(self):
        sub_urls = self.get_spages()
        post_urls = self.get_posts(sub_urls)
        user_urls = self.get_upages(post_urls)
        self.get_usubs(user_urls)

    # This method goes through each page of a subreddit, obtaining a url to each page and storing it in a list
    # subreddit_name - the name of the subreddit to search
    # page_count - The number of pages to go through and hence urls to obtain
    # return - a list of urls, one for each subreddit page
    def get_spages(self):
        self.collection_requests.find_one_and_update({'request': self.subreddit_name + "F"}, {'$set': {'pdone': 5.00}}, return_document=False)
        print("5.00% done")
        i = 1
        sub_urls = list()
        mainurl = 'https://www.reddit.com/r/' + self.subreddit_name
        nexturl = mainurl
        sub_urls.append(nexturl)

        while True:
            error_flag = False
            if i == self.page_count:
                break
            try:
                r = requests.get(nexturl, headers=self.headers)
                time.sleep(2)
            except:
                error_flag = True

            if error_flag:
                timeout = 1
            else:
                timeout = self.limit.timeout(r)

            if timeout == 0:
                subreddit = r.text.rstrip('\n')
                print("fetching next subreddit page...")
                count = str(i*25)
                nexturl = re.search(r'"https://www.reddit.com/r/' + self.subreddit_name + '/\?.+?(after=t3_.+?)"', subreddit).group(1)
                nexturl = mainurl + "/?count=" + count + "&" + nexturl

                sub_urls.append(nexturl)
                i += 1
            else:
                print("time out, fetching again...")

        return sub_urls

    # This method goes through each page url and extracts a url for each user submitted post
    # sub_urls - the list of page urls
    # return - a list of urls, one for each user submitted post
    def get_posts(self, sub_urls):
        self.collection_requests.find_one_and_update({'request': self.subreddit_name + "F"}, {'$set': {'pdone': 10.00}}, return_document=False)
        print("10.00% done")
        print(sub_urls)
        post_urls = list()
        i = 0

        while True:
            error_flag = False
            if i == len(sub_urls):
                break

            try:
                r = requests.get(sub_urls[i], headers=self.headers)
                time.sleep(2)
            except:
                error_flag = True

            if error_flag:
                timeout = 1
            else:
                timeout = self.limit.timeout(r)

            if timeout == 0:
                subreddithtml = r.text.rstrip('\n')
                print("fetching post urls of the next page...")
                post_urls = post_urls + re.findall(r'<li class="first"><a href="(.+?)"', subreddithtml)
                print(post_urls)
                i += 1
            else:
                print("time out, fetching again...")

        # go through list, check each url to see if it matches with one already in the database.
        # If it already exists in the database then remove it from the list
        cposts_urls = post_urls.copy()
        delete_count = 0
        for index, post_url in enumerate(cposts_urls):
            if self.collection_posts.find_one({'url': post_url}) is not None:
                del post_urls[index - delete_count]
                print("found, deleted")
                delete_count += 1
            else:
                aposturl = {'url': post_url}
                self.collection_posts.insert_one(aposturl)
                print("not found, adding to db")

        return post_urls

    # This method goes through each user submitted post extracting every user account url pertaining to a comment
    # post_urls - the list of user submitted posts
    # return - a set of urls, one for each user comments
    def get_upages(self, post_urls):
        user_urls = set()
        post_count = 0
        totalpostsize = len(post_urls)

        while True:
            error_flag = False
            if post_count == 3 or len(user_urls) > 35:
                break
            try:
                r = requests.get(post_urls[post_count], headers=self.headers)
                time.sleep(2)
            except:
                error_flag = True

            if error_flag:
                timeout = 1
            else:
                timeout = self.limit.timeout(r)

            if timeout == 0:
                html_post = r.text.rstrip('\n')
                pdone = (((100-(((len(post_urls) - post_count)/totalpostsize)*100))/2) + 10)
                self.collection_requests.find_one_and_update({'request': self.subreddit_name + "F"}, {'$set': {'pdone': pdone}}, return_document=False)
                print("%.2f%% done" % pdone)
                print("fetching every url account of next post...")
                user_urls = user_urls | set(re.findall(r'</a><a href="https://www.reddit.com/user/(.+?)"', html_post))
                print(user_urls)
                post_count += 1
            else:
                print("time out, fetching again...")
        return user_urls

    # This method queries all HTML source document from the specified collection and extracts the users subreddits
    def get_usubs(self, user_set):
        subsmapped = dict()
        subredditlist = list()
        top_list = list()
        totalusersize = len(user_set)
        currentusersize = totalusersize
        testtotal = list()

        for user in user_set:
            error_flag = True
            sub_counted = dict()
            pdone = (((100-((currentusersize/totalusersize)*100))/2)+50)
            self.collection_requests.find_one_and_update({'request': self.subreddit_name + "F"}, {'$set': {'pdone': pdone}}, return_document= False)
            print("%.2f%% done" % pdone)
            while error_flag:
                try:
                    error_flag = False
                    reddit_user = self.r.get_redditor(user)
                    for comment in reddit_user.get_comments(limit=100):
                        if subsmapped.get(comment.subreddit.display_name) is None:
                            subsmapped[comment.subreddit.display_name] = 1
                            sub_counted[comment.subreddit.display_name] = 1
                        else:
                            if sub_counted.get(comment.subreddit.display_name) is None:
                                subsmapped[comment.subreddit.display_name] += 1
                                sub_counted[comment.subreddit.display_name] = 1

                    currentusersize -= 1
                except:
                    error_flag = True

        print(testtotal)
        for k, v in subsmapped.items():
            subredditlist.append(SubReddit(k, v))
            subredditlist.sort(key=lambda x: x.count, reverse=True)
        print("Users from this subreddit also frequent the following subreddits: ")
        index = 0
        totalcount = 0
        for sub in subredditlist:
            if index == 25:
                    break
            if sub.getname() != self.subreddit_name and sub.getcount() >= 2 and self.low_subscriber(sub.getname()):
                index += 1
                totalcount += sub.getcount()
                print("%s %d" % (sub.getname(), sub.getcount()))
                top_list.append(sub.getname())
                top_list.append(sub.getcount())

        self.collection_topsubs.insert_one({'subreddit': self.subreddit_name, 'list': top_list})
        print("top subreddits stored in db")
        self.collection_requests.find_one_and_update({'request': self.subreddit_name + "F"}, {'$set': {'pdone': 100}}, return_document=False)
        print("updated pdone")

        if self.connection.llen('recent') == 10:
            self.connection.rpop('recent')

        self.connection.lpush('recent', self.subreddit_name)
        print(self.connection.lrange('recent', 0, -1))

    def low_subscriber(self, sub):
        high_subscriber = {'funny': True, 'AskReddit': True, 'pics': True, 'todayilearned': True, 'worldnews': True,
                           'science': True, 'IAmA': True, 'blog': True, 'videos': True, 'gaming': True, 'movies': True,
                           'Music': True, 'Music': True, 'aww': True, 'news': True, 'gifs': True, 'technology': True,
                           'askscience': True, 'explainlikeimfive': True, 'bestof': True, 'Earthporn': True, 'WTF': True,
                           'books': True, 'television': True, 'AdviceAnimals': True, 'LifeProTips': True, 'sports': True,
                           'mildlyinteresting': True, 'DIY': True, 'politics': True, 'Fitness': True, 'Showerthoughts': True,
                           'space': True, 'Jokes': True, 'tifu': True, 'food': True, 'photoshopbattles': True,
                           'InternetIsBeautiful': True, 'GetMotivated': True}

        if sub in high_subscriber:
            return False
        else:
            return True