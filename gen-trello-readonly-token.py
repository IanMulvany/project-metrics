"""
Generarte a user token to allow an application to get a
read-only token for the user's private boards, that
has no expiration.

Uses OAuth enabled Requests.

"""

import requests
from collections import namedtuple
from oauth_hook import OAuthHook

### get authentication strings from local file 
# would probably be better as a simple config file as a python struct that I imported.

trello_auth_info = "/Users/ian/code/public-code/project-metrics/trello-credentials.txt"
TrelloKeys = namedtuple('Keys', "key secret")

def get_value_from_line(line):
	value = line.split(":")[1].strip()
	return value 

def get_keys(keys_file, myTuple):
	lines = open(keys_file, 'r').readlines()
	values = []
	expected_number_of_fields = len(myTuple._fields)
	for i in range(expected_number_of_fields):
		part = get_value_from_line(lines[i])
		values.append(part)
	thisTuple = myTuple._make(values)
	return thisTuple
	
TrelloAuth = get_keys(trello_auth_info, TrelloKeys)

def parse_qs(response):
	print response
	items = {}
	parts = response.split('&')
	for part in parts:
		key_val = part.split("=")
		items[key_val[0]] = key_val[1]
	return items

# 3 legged OAuth

# OAuth 1st leg
# make inital request with consumer key and consumer secret, parse the response
trello_oauth_hook = OAuthHook(consumer_key=TrelloAuth.key, consumer_secret=TrelloAuth.secret)
payload = {'expiration':'1day', 'scope':'scope=read,write'}# response_type=token&}
response = requests.post('https://trello.com/1/OAuthGetRequestToken', hooks={'pre_request': trello_oauth_hook})#, params=payload)
qs = parse_qs(response.text)
oauth_token = qs['oauth_token']
oauth_secret = qs['oauth_token_secret']

# OAuth 2nd leg
# direct the user to accept the authorisation request, accept their key
# this request is read only
# it never expires 
print "Go to https://trello.com/1/OAuthAuthorizeToken?expiration=never&oauth_token=%s allow the app and copy your PIN" % oauth_token
oauth_verifier = raw_input('Please enter your PIN:')

# OAuth 3rd leg
# make request with oauth_verifier, parse respnse for final token
new_trello_oauth_hook = OAuthHook(oauth_token, oauth_secret, consumer_key=TrelloAuth.key, consumer_secret=TrelloAuth.secret)
response = requests.post('https://trello.com/1/OAuthGetAccessToken', {'oauth_verifier': oauth_verifier}, hooks={'pre_request': new_trello_oauth_hook})
response = parse_qs(response.content)
final_token = response['oauth_token']
final_token_secret = response['oauth_token_secret']

# list a users's boards to test that we have the application working.
url = "https://trello.com/1/members/my/boards"
payload = {'key':TrelloAuth.key, 'token':final_token}
r = requests.get(url, params=payload)
print r.url
print r.status_code
print r.headers
print r.json

# print the auth token so we can store it for later use
print ""
print 'final_token: ', final_token
print 'final_token_secret:', final_token_secret