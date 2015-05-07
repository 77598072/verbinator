verbinator
Web verb case tampering program for penetration testing

Verbinator provides the ability to test web server response to all RFC and documented non-RFC web verbs. The ability to use an arbitrary text string as a verb is also supported. 

Web server responses can be manually viewed or a diff can be performed against the upper and lower case verb responses.

Usage:
./verbinator.py or python verbinator.py
All arguments are optional
-h --help        help and usage info

-u --URL         list of one or more URLs
-f --URLFILE     path/filename containing list of URLS
                 -> blank lines are handled
                 -> multiple URLs per line ok if separated by blank space(s)
                 -> URLs assumed to be correctly formatted, e.g. www.google.com
                 -> parser gracefully exits if filename is invalid
(default is example.com)

-p --http-only   perform a scan using HTTP only
-s --https-only  perform a scan using HTTPS only
(default is perform scan using both HTTP and HTTPS)

-a --arbs        list of one or more verbs
(default is      **RFC 2616**                     'OPTIONS', 'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE', 'CONNECT',
                 **RFC 2518**                     'PROPFIND', 'PROPPATCH', 'MKCOL', 'COPY', 'MOVE', 'LOCK', 'UNLOCK',
                 **RFC 3252**                     'VERSION-CONTROL', 'REPORT', 'CHECKOUT', 'CHECKIN', 'UNCHECKOUT', 'MKWORKSPACE', 'UPDATE', 'LABEL', 'MERGE', 'BASELINE-CONTROL', 'MKACTIVITY',
                 **RFC 3648**                     'ORDERPATCH',
                 **RFC 3744**                     'ACL',
                 **draft-dusseault-http-patch**   'PATCH',
                 **draft-reschke-webdave-search** 'SEARCH',
                 **Microsoft WebDAV**             'BCOPY' 'BDELETE', 'BMOVE', 'BPROPFIND', 'BPROPPATCH', 'NOTIFY', 'POLL', 'SUBSCRIBE', 'UNSUBSCRIBE', 'X-MS-ENUMATTS',
                 **Microsoft RPC extensions**     'RPC_OUT_DATA', 'RPC_IN_DATA')

-d --diff        Compare upper and lower case verb responses
(default is False)

-n --num         Port number
(default is '')   
