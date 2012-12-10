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
trello_user_auth_code = "/Users/ian/code/public-code/project-metrics/trello-readonly-token.txt"
TrelloKeys = namedtuple('Keys', "key secret")
UserAuth = namedtuple('Auth', "key")

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
UserAuth = get_keys(trello_user_auth_code, UserAuth)

def parse_qs(response):
	print response
	items = {}
	parts = response.split('&')
	for part in parts:
		key_val = part.split("=")
		items[key_val[0]] = key_val[1]
	return items

# list a users's boards to test that we have the application working.
# we already have the author token from a previous script that ran. 
url = "https://trello.com/1/members/my/boards"
payload = {'key':TrelloAuth.key, 'token':UserAuth.key}
r = requests.get(url, params=payload)
print r.url
print r.status_code
print r.headers
print r.json

