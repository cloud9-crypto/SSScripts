import requests

#hosts
hosts = []
hosts.append("https://webservices.massmutual.com")
hosts.append("https://webservicesv2.massmutual.com")
hosts.append("https://webservicesv3.massmutual.com")
hosts.append("https://apis-r.massmutual.com")
hosts.append("https://apis.massmutual.com")
hosts.append("https://mobile-webservices.massmutual.com")

#apis
apis = ["agreementsapi","bpbills","bpdetails","bppac","agreement","agmtproducer","routingnbr","alertsapi","bankvalapi","bankval","catseventsapi","beneficiaryapi","beneaddldatams","billing","wpobusinessservices","wpoparticipants","wpoplan","contentapi","directorycldapms","ccpayment","customersapi","customers/v1/addresses","customers/v1/agreements","bemmanagerapi","customers/v1/bem","customers/v1/cores","customers/v1/emails","identityapi","customers/v1/ids","customers/v1/names","customers/v1/phones","customers/v1/preferences","customers/searchmatch","digitalclientprofile","ecorrespondenceapi","ecorrespondencems","esso","catsevents","eventsapi","disabilityclaimsapi","finhistoryapi","finhistory","html2pdfapi","leadsapi","leadsms","loans","loandetails","lockboxaddr","pacapi","","privacyapi","producersapi","producers/coresdl","restrictionsdl","restrictions","restrictions/restrictionstd","retiresmartamc1","retiresmartamc","flowcontrol","suitabilityapi","suitabilitycasems","suitabilitycommentms","suitabilitycontactms","suitabilitydropdownsms","suitabilityeventms","suitabilityquestionms","suitabilityresultms","suitabilityuserms","addresstransactionapi","tradvloans","uspsms","dataanalyticsapi","alertsms"]

results = []

for api in apis:
    for host in hosts:
        entry = {}
        entry["url"] = "{0}/rest/{1}".format(host,api)
        try:
            resp = requests.get(entry["url"], verify=False)
            entry["resp"] = str(resp)
        except requests.exceptions.SSLError: 
            entry["resp"] = "SSLError"
        except requests.exceptions.ReadTimeout:
            entry["resp"] = "Timeout"
        except requests.exceptions.ConnectionError:
            entry["resp"] = "ConnectionError"
        results.append(entry)

print(results)