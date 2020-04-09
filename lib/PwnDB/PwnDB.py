#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, time, random
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from core.colors import colors

def haveIBeenPwned(email):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    cookies = {
        '__cfduid': 'db69bfd7ae01e4d5d3c3f1e9c8a89bff41585353125',
        'ai_user': '5Ner1|2020-03-27T23:52:08.257Z',
        '_ga': 'GA1.2.1775275446.1585353129',
        '_gid': 'GA1.2.1675250400.1585501117',
        'ai_session': 'ZPXdR|1585501117405|1585503143569',
        'Searches': '7',
        'BreachedSites': '28',
        'Pastes': '0',
    }

    headers = {
        'Host': 'haveibeenpwned.com',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'https://haveibeenpwned.com/',
        'X-Requested-With': 'XMLHttpRequest',
        'Request-Id': '|DOpkD.junPv',
        'Request-Context': 'appId=cid-v1:bcc569a3-d364-4306-8bbe-83e9fe4d020e',
        'Connection': 'close',
    }

    print(colors.info + " Searching information about Leaks found :)" + colors.end)

    try:
        response = requests.get('http://haveibeenpwned.com/unifiedsearch/'+str(email), headers=headers, cookies=cookies, verify=False)

        infoAboutLeak = []
        items = json.loads(response.text)
        breaches = items['Breaches']

        for breache in breaches:
            name = breache['Name']
            domain = breache['Domain']
            date = breache['BreachDate']
            infoAboutLeak.append(json.dumps({'name': name, 'domain': domain, 'date': date}))
    except:
        infoAboutLeak.append("Sources not found")
    
    return infoAboutLeak
        
def parsePwndbResponse(mail,text):
    if "Array" not in text:
        return None

    leaks = text.split("Array")[1:]
    emails = []
    foundLeak = False

    for leak in leaks:
        leaked_email = ''
        domain = ''
        password = ''
        try :
            leaked_email = leak.split("[luser] =>")[1].split("[")[0].strip()
            domain = leak.split("[domain] =>")[1].split("[")[0].strip()
            password = leak.split("[password] =>")[1].split(")")[0].strip()
        except:
            pass
        if leaked_email != "donate" and domain != "btc.thx" and password != "12cC7BdkBbru6JGsWvTx4PPM5LjLX8g":
            foundLeak = True
            emails.append(json.dumps({'username': leaked_email, 'domain': domain, 'password': password}))
    
    if foundLeak:
        emails.append(haveIBeenPwned(mail))

    return emails

session = requests.session()
session.proxies = {'http': 'socks5://127.0.0.1:9050', 'https': 'socks5://127.0.0.1:9050'}

def findLeak(emails):

    url = "http://pwndb2am4tzkvold.onion/"
    leaks = []
    
    print(colors.info + " Searching Leaks :)" + colors.end)
    for email in emails:

        x = json.loads(email)
        mail = x['email']
        userInstagram = x['user']
        userID = x['userID']
        username = mail.split("@")[0]
        domain = mail.split("@")[1]

        request_data = {'luser': username, 'domain': domain, 'luseropr': 1, 'domainopr': 1, 'submitform': 'em'}
        time.sleep(1)
        response = session.post(url, data=request_data)
        print(colors.info + " Searching: " + mail + colors.end)
        if response.status_code == 200:
            target = {'user': userInstagram, 'userID': userID, 'email': mail, 'leak': parsePwndbResponse(mail,response.text)}
            leaks.append(target)
            print(colors.good + " The request was successful" + colors.end)
        else:
            print(colors.bad + " The request was not successful for the user: " + colors.W + userInstagram + colors.R + "and email: " + colors.W + email + colors.R + ". Maybe you should increase the delay" + colors.end)

    return leaks

def saveResultsPwnDB(results):
    with open("PwnDBResults.txt", "a") as resultFile:
        for result in results:
            leak = result.get("leak")
            if len(leak) >= 1:
                print(colors.good + " User: " + colors.M + result.get("user") + colors.B + " Email: " + colors.M + result.get("email") + colors.M + " Have Leaks " + colors.end)
                resultFile.write("User: " + result.get("user") + " Email: " + result.get("email")+"\n")
                for i in range (len(leak)-1):
                    print("\t" + colors.good + " Leaks found in PwnDB: " + colors.M + str(leak[i]) + colors.end)
                    resultFile.write("\t" + "Leaks found in PwnDB: " + str(leak[i]) + "\n")

                haveIBeenPwnedInfo = leak[-1]
                print("\t\t" + colors.info + " Information found in HaveIBeenPwned from pwned websites" + colors.end)
                for infoPwned  in haveIBeenPwnedInfo:
                    print("\t\t" + colors.good + colors.M + infoPwned + colors.end)
                    resultFile.write("\t\t" + infoPwned + "\n")
            else:
                print(colors.good + " User: " + colors.W + result.get("user") + colors.B + " Email: " + colors.W + result.get("email") + colors.B + " Not Have Leaks in PwnDB" + colors.end)
    resultFile.close()


