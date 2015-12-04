Reddit Connect v1.0

What is this Project about?
Reddit Connect is a web app made for the community of https://reddit.com. If you dont know what Reddit is, you can find out by clicking here https://en.wikipedia.org/wiki/Reddit. In short Reddit is a website that hosts individual communities, where each community is about a specific topic for users to discuss on. As an example let's consider the community called WebDev. This community discusses anything related to Web Development. With Reddit being as big as it is  there may be many other communities that are related to the WebDev community but serves a much more specific role for discussion. Some of these closely related but much more specific communities are JavaScript, Porgramming, Web_design, Python, Linux, Frontend, ProgrammerHumor, PHP, LearnProgramming, LearnJavaScript, and many more! A user on WebDev may not know that these communities exists and this is exactly where Reddit Connect comes in. Type in your favorite community and it i'll find related communities.

What must i download in order to get this to work on my own server?
Reddit Connect makes use of various APIs and databases. All APIs can be installed by running the setup.py file. The databases used are MongoDB and Redis. They must be manually installed and can be downloaded from:
https://www.mongodb.org/downloads#production
http://redis.io/download

If for whatever reason setup.py doesn't install all APIs needed you will have to manually install them with pip install: http://python-packaging-user-guide.readthedocs.org/en/latest/installing/. The needed APIs are Django, praw, pymongo, requests, wikipedia, redis. To check for missing APIs type pip freeze in your terminal.
How do i get this running?
Step 1: For Redis run redis-server.
Step 2: For MongoDB run mongod.
Step 3: For the Django server/backend run manage.py

Important commands:
For Redis you can run redis-cli. The two most important commands for running purposes is SHUTDOWN. If you exit out of the redis-server without properly closing it down you may run into issues next time it starts up again. To fix this simply run redis-cli and type SHUTDOWN to properly shutdown the redis server.

For MongoDB run mongo. The most important command for running purposes is db.dropDatabase(). If you stop the Django server/backend in the middle of it processing a request and next time run it again to process that same request, you may run into an issue. To fix this you can simply drop the database by typing use Reddit_Link and then db.dropDatabase().

My to-do list for v2.0:
*Let moderators log in and request a more accurate rundown of related subreddits. The backend will process these requests whenever resources are free.

*Add Django session.

*Setup a relational database for the storage of user information and session.

*Refactoring and more error checking.

*Make requests from the browser side in parallel with that of the backend in order to increase the search processing speed.

*Use OAuth for the Reddit API in order to be able to make requests more frequently. Currently non OAuth is capped at 2 seconds per requests, OAuth is capped at 1 second per request.

*Revamp the UI from using AngularJS to introducing a more streamlined CSS layout.
