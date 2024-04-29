#!/usr/bin/env python

# Author: Brandon Frelich
# Version x.01 Basic POC validation.
# - some possible to do's
# -- move credentials to cli option?
# -- configure logging and toggle level of logging based on debug values
# -- add in try: functionality to prevent eav from returning something when an error occurs

import argparse
import sys
import requests
import json
import urllib3
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

########################################################################
# CHANGEME TO A SERVICE ACCOUNT THAT CAN READ THE GTM SERVERS STATE    #
########################################################################

user = "service"
passwd = "XXXXXsupersecretXXXXX"

#Setup command line arguments using Python argparse
parser = argparse.ArgumentParser(description='EAV to monitor gtm pool member state')
# First two arguments passed by EAV are the base pool and port number of the LTM pool member will be needed for logging?
parser.add_argument('pool')
parser.add_argument('port')
# Next three arguments must be passed by the EAV monitor configuration
parser.add_argument('--bigip', '-b', help='IP or hostname of the gtm server object (which can be an LTM)', required=True)
parser.add_argument('--gtmserver', '-g', help='IP or hostname of GTM Management or Self IP', required=True)
parser.add_argument('--vip', '-v', help='vip name ~Common is assumed', required=True)

args = parser.parse_args()

contentTypeJsonHeader = {'Content-Type': 'application/json'}

#adapted from https://devcentral.f5.com/articles/demystifying-icontrol-rest-6-token-based-authentication
def get_auth_token():
    payload = {}
    payload['username'] = user
    payload['password'] = passwd
    payload['loginProviderName'] = 'tmos'
    authurl = 'https://%s/mgmt/shared/authn/login' % args.gtmserver
    token = bip.post(authurl, headers=contentTypeJsonHeader, auth=(user, passwd), data=json.dumps(payload)).json()['token']['token']
    #token = bip.post(authurl, headers=contentTypeJsonHeader, auth=(user, passwd), data=json.dumps(payload)).json()
    #print token
    return token

#So max outstanding auth tokens is 100. If you don't delete them they will be quickly used up.
def del_auth_token(authtoken):
    url = 'https://%s/mgmt/shared/authz/tokens/%s' % (args.gtmserver, authtoken)
    headers = {
        'Content-Type': 'application/json',
        'X-F5-Auth-Token': authtoken
    }
    delresp = requests.delete(url,headers=headers, verify=False)
    logging.warning(json.dumps(delresp.json(), indent=4))

bip = requests.session()
bip.verify = False
authtoken = get_auth_token()

def getGTMserver(authtoken):
    url = 'https://%s/mgmt/tm/gtm/server/~Common~%s/virtual-servers/~Common~%s' % (args.gtmserver, args.bigip, args.vip)
    #url = 'https://%s/mgmt/tm/gtm/server/~Common~%s/' % (args.gtmserver, args.bigip)
    headers = {
        'Content-Type': 'application/json',
        'X-F5-Auth-Token': authtoken
    }
    #print(headers)
    resp = requests.get(url,headers=headers, verify=False)
    #print(json.dumps(resp.json(), indent=4))
    logging.warning(json.dumps(resp.json(), indent=4))

    # Condition within in json is if the key "enabled" exists (and value = true) the virtual server is considered up and enabled
    # False condition is that the key "disabled" exists (and value = true). The responsible party has been sacked.

    if "enabled" in resp.json():
        print "UP"
        logging.info('UP')
    else:
    	pass

getGTMserver(authtoken)
del_auth_token(authtoken)
