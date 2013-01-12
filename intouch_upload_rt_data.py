"""
IntouchId client for uploading real time data for the logged in user

Copyright (c) 2012 Sarang Lakare, *sarang


How to use:

# inialize class object
rtd = intouch_upload_rt_data.RealTimeDataTx()
# login to server (once only..)
rtd.login(<intouchid>, <passwd>)

# Prepare and upload data to server 
rt_data = dict()
rt_data['speed'] = 35
rt_data['height'] = 1233

# Upload to server
rtd.upload_rt_info(rt_data)

#... do this as many times as you want ...

# logout from server (at the end...)
rtd.logout()

"""
import getpass
import time
import datetime
import subprocess
import httplib
import urllib
import oauth.oauth as oauth
import pdb, traceback, sys
import string
import base64
import simplejson
import socket
import fcntl
import struct

# Main server
#SERVER = 'mycontactidbeta.appspot.com'

# Test server
SERVER = 'mciapitest-hrd.appspot.com'

# Local server
#SERVER = '192.168.2.10'
#SERVER = 'localhost'

# Port for connection
PORT = 80
# PORT = 443
# PORT = 8000

# fake urls for the test server (matches ones in server.py)
REQUEST_TOKEN_URL = 'http://'+SERVER+':'+str(PORT)+'/api/oauth/request_token/'
DIRECT_ACCESS_TOKEN_URL = 'http://'+SERVER+':'+str(PORT)+'/api/basic/direct_access_token/'
RT_UPLOAD_URL = 'http://'+SERVER+':'+str(PORT)+'/api/v1/upload_rt_info/'
TOKEN_RELEASE_URL = 'http://'+SERVER+':'+str(PORT)+'/api/btaasic/release_token/'

# key and secret granted by the service provider for this consumer application
CONSUMER_KEY = 'gLz6bqkuTm8vLLbbDx'

USER_AGENT = 'IntouchId Python Client ver 1.0'

# Store token
ACCESS_TOKEN = ''

class FileData():
    
    #for mac address
    def getHwAddr(self):
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', 'wlan0'[:15]))
      return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]
    #for IP address 
    def ipaddress(self):
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      s.connect(("gmail.com",80))
      ip=s.getsockname()[0]
      return ip
    #This file gives Charging status of Battery
    def charging_state(self):
      f=open('/proc/acpi/battery/BAT0/state','r')
      for line in f:
	if 'charging state' in line:
	  if 'charging' in line:
	    return 'charging'
	  else:
	    return 'discharging'
	    
	    
    #This file contains the length of time since the system was booted, as well as the amount of time since then that the system has been idle. Both are given as floating-point values, in seconds
    def uptime(self):
      f=open('/proc/uptime','r')
      for line in f:
	return line
	
    #gives information about current_user logged in to system
    def current_user(self):
      a=getpass.getuser()
      return a
      
    #gives memory and CPU usage
    def usage(self):
        """Return int containing memory used by user's processes."""
        uname=self.current_user()
        self.process = subprocess.Popen("ps -u %s -o rss | awk '{sum+=$1} END {print sum}'" % uname,
                                        shell=True,
                                        stdout=subprocess.PIPE,
                                        )
        self.stdout_list = self.process.communicate()[0].split('\n')
        return int(self.stdout_list[0])
	
	    
class RealTimeDataTx():
    access_token = ''

    def login(self, username, passwd):
        self.access_token = self.obtain_trusted_access_token(username, 'test123')

    def obtain_trusted_access_token(self, user_name, user_password, http_method='POST'):
        auth_header = 'Basic ' + string.strip(base64.encodestring(user_name + ':' + user_password))
        parameters = {'consumer_key':CONSUMER_KEY}
        params = urllib.urlencode(parameters)
        connection = httplib.HTTPConnection("%s:%d" % (SERVER, PORT))
        if http_method == 'GET':
            connection.request(http_method, DIRECT_ACCESS_TOKEN_URL+ "?" + params, headers={'Authorization': auth_header}) 
        elif http_method == 'POST':
            connection.request(http_method, DIRECT_ACCESS_TOKEN_URL, params, headers={'Authorization': auth_header}) 
        else:
            raise 'UnknownHttpMethod'
        resp = connection.getresponse()
        
        print '\tResponse http status: ' + unicode(resp.status)
        if resp.status != 200:
            print '\tResponse failed.'
            return None
        else:
            resp = resp.read()
        resp_dict = simplejson.loads(resp)
        if resp is None:
            print '\tError: No response recieved. Possibly some error on server.'
            return None
        # Check the status
        if resp_dict.get('status') == 'error':
            # something went wrong
            print '\tError getting token. Message: ' + resp_dict.get('message')
            return None
        
	print 'Token: ' + resp_dict.get('token')
        # return the actual token
        return resp_dict.get('token')        


    def upload_rt_info(self, rt_data):
        '''
        Uploads real time data. The data should be a dictionary of name value pairs.
        Example:
        {
            'height': 3455, 
            'speed': 45
        }

        Returns None on error and the response from server on success
        '''
        json_to_send = simplejson.dumps(rt_data)
        auth_header = 'Basic ' + string.strip(base64.encodestring(CONSUMER_KEY + ':' + self.access_token))
        connection = httplib.HTTPConnection("%s:%d" % (SERVER, PORT))

        connection.request('POST', RT_UPLOAD_URL, json_to_send, headers={'Authorization': auth_header, 'Content-Type':'application/json', 'User-Agent':USER_AGENT}) 
        resp = connection.getresponse()

        print '\tResponse http status: ' + unicode(resp.status)
        if resp.status != 200:
            print '\tResponse failed.'
            return None
        else:
            resp = resp.read()
            resp_dict = simplejson.loads(resp)
            print '\tServer status: ' + unicode(resp_dict.get('status', ''))
            print '\tServer message: ' + unicode(resp_dict.get('message', ''))
            return resp_dict
        
        
    def logout(self):
        '''
        release the token. Returns the http response.
        '''
        # setup
        # username should be CONSUMER_KEY and passwd should be the token
        auth_header = 'Basic ' + string.strip(base64.encodestring(CONSUMER_KEY + ':' + self.access_token))
        connection = httplib.HTTPConnection("%s:%d" % (SERVER, PORT))
        connection.request(http_method, TOKEN_RELEASE_URL, headers={'Authorization': auth_header}) 
        return connection.getresponse()

    def pause():
        print ''
        time.sleep(1)

if __name__ == '__main__':
    print 'Done.'
  
fl=FileData()
cs=fl.charging_state()  #charging status of computer
ut=fl.uptime()          #uptime: the timr for ehich system is on from and from then till what it was idle
usr=fl.current_user()
muse=fl.usage()
ipa=fl.ipaddress()
mac=fl.getHwAddr()
obj=RealTimeDataTx()

obj.login("90009009","test123")
obj.upload_rt_info( {
            'Charging state': cs, 
            'Uptime': ut,
            'Current User': usr,
            'Memory Used by Current Users Processes':muse,
            'IP Address':ipa,
            'MAC Address':mac
        }) 