# mydyndns
REST server/client to manage dynamic dns leases

Currently a skeleton, the idea is to save the config to disk (sqlite3?) and connect to a proper DNS server using rndc, keeping this as simple as possible.

This is the expected output of it's client:
```
$ python ./client.py create testdns $ADMINPWD
HA4MO0M4FK2TET8BUL7TTBEGDEQ6UY

$ python ./client.py update testdns HA4MO0M4FK2TET8BUL7TTBEGDEQ6UY
Domain updated
```

Server:
```
$ python ./server.py
27/02/2018 18:38:07 INFO: Listening to port 5000
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
27/02/2018 18:38:20 DEBUG: {u'domain': u'testdns', u'password': u'insecure'}
27/02/2018 18:38:20 INFO: test3 is not a registered domain
127.0.0.1 - - [27/Feb/2018 18:38:20] "POST /api/domain/create HTTP/1.1" 200 -
27/02/2018 18:38:38 INFO: Domain "testdns" update requested
27/02/2018 18:38:38 INFO: Domain "testdns" updated with ip "127.0.0.1"
127.0.0.1 - - [27/Feb/2018 18:38:38] "POST /api/domain/update HTTP/1.1" 201 -
```
