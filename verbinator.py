#!/usr/bin/python
#Check for valid websites verbs form the following RFC's
#2616, 2518, 3253, 3648, 3744
#draft--dusseault-http-patch, draft-reschke-webdav-search
#
#Microsoft WebDAV methods are also included
#
#Shad Malloy, init 2/25/2015
#
#Leigh Fanning, update 3/6/2015
#
#Imports
import argparse
import httplib2
import signal
import sys
import os
from os import path, access, remove

#CTRL+C Handler
def customExit(signum, frame):
    #restore the original to prevent problems
    signal.signal(signal.SIGINT, originalSigint)
    
    #End message
    print ('Verb Scan Cancelled')

    #exit
    sys.exit(1)

# Make the parser
#
# All arguments are optional
#
# [--URL | --URLFILE]
# -u --URL         list of one or more URLs
# -f --URLFILE     path/filename containing list of URLS
#                  -> blank lines are handled
#                  -> multiple URLs per line ok if separated by blank space(s)
#                  -> URLs assumed to be correctly formatted, e.g. www.google.com
#                  -> parser gracefully exits if filename is invalid
# (default is example.com)
#
# [-http-only | -https-only]
# -p --http-only   perform a scan using HTTP only
# -s --https-only  perform a scan using HTTPS only
# (default is perform scan using both HTTP and HTTPS)
#
# [--arbs]
# -a --arbs        list of one or more verbs
# (default is      **RFC 2616**                     'OPTIONS', 'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE', 'CONNECT',
#                  **RFC 2518**                     'PROPFIND', 'PROPPATCH', 'MKCOL', 'COPY', 'MOVE', 'LOCK', 'UNLOCK',
#                  **RFC 3252**                     'VERSION-CONTROL', 'REPORT', 'CHECKOUT', 'CHECKIN', 'UNCHECKOUT', 'MKWORKSPACE', 'UPDATE', 'LABEL', 'MERGE', 'BASELINE-CONTROL', 'MKACTIVITY',
#                  **RFC 3648**                     'ORDERPATCH',
#                  **RFC 3744**                     'ACL',
#                  **draft-dusseault-http-patch**   'PATCH',
#                  **draft-reschke-webdave-search** 'SEARCH',
#                  **Microsoft WebDAV**             'BCOPY' 'BDELETE', 'BMOVE', 'BPROPFIND', 'BPROPPATCH', 'NOTIFY', 'POLL', 'SUBSCRIBE', 'UNSUBSCRIBE', 'X-MS-ENUMATTS',
#                  **Microsoft RPC extensions**     'RPC_OUT_DATA', 'RPC_IN_DATA')
#
# [--diff]
# -d --diff        Compare upper and lower case verb responses
# (default is False)
#
# [--num]
# -n --num         Port number
# (default is '')   
#              
def verbinatorCommandLineParser():

    main_parser = argparse.ArgumentParser(
        prog='verbinator', 
        description='******* * * * * * * * CHECK WEBSITE VERBS * * * * * * * *******',
        epilog='******* * * * * * * * * * * * * * * * * * * * * * * * * *******')

    input_options_group = main_parser.add_mutually_exclusive_group()
    input_options_group.add_argument('-u', '--URL', nargs='+', help="URL(s) to check")
    input_options_group.add_argument('-f', '--URLFILE', nargs=1, type=argparse.FileType('r'), help="file containing list of URL(s) to check")

    http_options_group = main_parser.add_mutually_exclusive_group()
    http_options_group.add_argument('-p', '--http-only', action='store_true', help="only HTTP scan")
    http_options_group.add_argument('-s', '--https-only', action='store_true', help="only HTTPS scan")

    main_parser.add_argument('-a', '--arbs', nargs='+', help="arbitrary verb(s)")
    main_parser.add_argument('-d', '--diff', default='False', action='store_true', help="compare verb case responses")
    main_parser.add_argument('-n', '--num', nargs=1, default='', help="use non-standard port")
    main_parser.add_argument('-version', action='version', version='%(prog)s 0.1')

    return main_parser

# Perform the method request on the site
def doCheck(connectionObject, connType, site, portNum, verb, diffFlag):

    (uresp_headers, ucontent) = connectionObject.request(connType + '://' + site + portNum, verb.upper())
    (lresp_headers, lcontent) = connectionObject.request(connType + '://' + site + portNum, verb.lower())

    if diffFlag is True:
   
        print ('***** ' + verb + ' Differential analysis ' + connType.upper() + ' ' + site + ' *****')

        #Remove the date field from the response. The date field contains the time/date and changes during the responses.
        uresp_headersList = str(uresp_headers).split(",")
        del uresp_headersList[5:7]
        lresp_headersList = str(lresp_headers).split(",")
        del lresp_headersList[5:7]
                                
        #Convert list to set, compare values for equality
        if set(uresp_headersList) == set(lresp_headersList):
            print ('Header responses for '+ verb + ' are the same for ' + connType.upper() + ' on ' + site)
        else:
            print ('Header responses are not the same for ' + verb.upper() + ' and ' + verb.lower() + ' this is interesting ' + connType.upper() + ' on ' + site)
        if ucontent == lcontent:
            print ('Content responses for '+ verb + ' are the same ' + connType.upper() + ' on ' + site)
        else:
            print ('Content responses are not the same for ' + verb.upper() + ' and ' + verb.lower() + ' this is interesting ' + connType.upper() + ' on ' + site)

    else:

        print ('***** '+ verb.upper() + ' for ' + site + ' *****')
        print (uresp_headers)
        print (ucontent)
        print ('***** '+ verb.lower() + ' for ' + site + ' *****')
        print (lresp_headers)
        print (lcontent)

#Main
def main(argv):
    
    # Create a parser and collect input arguments
    parser = verbinatorCommandLineParser()
    args = parser.parse_args()

    # Set options per input arguments
    if (args.http_only):
        httpFlag = True
        httpsFlag = False
    elif (args.https_only):
        httpFlag = False
        httpsFlag = True
    else:
        httpFlag = True
        httpsFlag = True
  
    if (args.URL):
        scanURLs = args.URL
    elif (args.URLFILE):
        filestr = (args.URLFILE[0]).read().split('\n')
        scanURLs = [x for x in filestr if x != '']
        (args.URLFILE[0]).close()
    else:
        scanURLs = ['example.com']

    if (args.arbs):
        verbList = args.arbs
    else:
        verbList = ['OPTIONS' , 'GET' , 'HEAD' , 'POST' , 'PUT' , 'DELETE' , 'TRACE' , 
                    'CONNECT' , 'PROPFIND' , 'PROPPATCH' , 'MKCOL' , 'COPY' , 'MOVE' , 'LOCK' , 
                    'UNLOCK' , 'VERSION-CONTROL' , 'REPORT' , 'CHECKOUT' , 'CHECKIN' , 'UNCHECKOUT' , 
                    'MKWORKSPACE' , 'UPDATE' , 'LABEL' , 'MERGE' , 'BASELINE-CONTROL' , 'MKACTIVITY' , 
                    'ORDERPATCH' , 'ACL' , 'PATCH' , 'SEARCH' , 'BCOPY' , 'BDELETE' , 'BMOVE' , 
                    'BPROPFIND' , 'BPROPPATCH' , 'NOTIFY' , 'POLL' , 'SUBSCRIBE' , 'UNSUBSCRIBE' , 
                    'X-MS-ENUMATTS' , 'RPC_OUT_DATA' , 'RPC_IN_DATA']

    if args.diff:
        diffFlag = args.diff
    else:
        diffFlag = False

    if args.num:
        portNum = args.num
    else:
        portNum = ''

    # dump collected arguments and options settings
    #print(args)
    #print("httpFlag is: ",httpFlag)
    #print("httpsFlag is: ",httpsFlag)
    #print("scanURLs is: ",scanURLs)
    #print("verb list is: ",verbList)
    #print("diffFlag is: ",diffFlag)
    #print("portNum is: ",portNum)
    
    connection = httplib2.Http()

    for site in scanURLs:
        print('checking site: ' + site)
        if httpFlag:
            try:
                response, content = connection.request('http://' + site + portNum)
                # proceed if we received a valid response
                if response.status == 200:
                    for verb in verbList:
                        doCheck(connection,'http',site,portNum,verb,diffFlag)
            except:
                print("Failed to connect to HTTP site")
                etype, emessage, traceback = sys.exc_info()
                print("Exception: ", etype, ' ', emessage)
        if httpsFlag:
            try:
                response, content = connection.request('https://' + site + portNum)
                # proceed if we received a valid response
                if response.status == 200:
                    for verb in verbList:
                        doCheck(connection,'https',site,portNum,verb,diffFlag)
            except:
                print("Failed to connect to HTTPS site")
                etype, emessage, traceback = sys.exc_info()
                print("Exception: ", etype, ' ', emessage)
                                    
#Custom Handler and Main
if __name__ == "__main__":
    #store original SIGINT handler
    originalSigint = signal.getsignal(signal.SIGINT)
    #use custom CTRL+C handler
    signal.signal(signal.SIGINT, customExit)
    #call main
    main(sys.argv[1:])
