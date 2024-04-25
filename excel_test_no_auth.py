import getpass
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import os

#from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings()\
    
def generate_api_key(firewall_ip, username, password):
    url = f"https://{firewall_ip}/api/?type=keygen&user={username}&password={password}"
    response = requests.get(url, verify=False)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        api_key = root.find('.//key').text
        return api_key
    else:
        print(f"Failed to generate API key from {firewall_ip}. Status code: {response.status_code}")
        return None
   
def get_con_devices():
 
 
    #username = input("Please enter the username: ")
    #password = getpass.getpass(prompt="Please enter the password: ")
    username = ""
    password = ""
   
   
    with open('panoramas.txt','r', encoding="utf-8") as file:
        panoramas = file.read().splitlines()
   
    rest_url = "/api/?type=op&cmd=<show><devices><connected></connected></devices></show>"
 
   
    for pan in panoramas:
        api_key = generate_api_key(pan, username, password)
        url = "https://" + pan + rest_url + "&key=" + api_key
        print(pan)
       
 
        resp = requests.get(url, verify=False)
        xmldata = ET.fromstring(resp.content)
           
        # Settings columns and rows
        cols = ["Hostname", "Serial Number", "Model", "Software Version", "App Version", "AV Version", "WildFire Version"]
        rows = []
 
        for el in xmldata.iter('entry'):
            hostname = el.findtext("hostname")
            serial = el.findtext("serial")
            model = el.findtext("model")
            swversion = el.findtext("sw-version")
            appversion = el.findtext("app-version")
            avversion = el.findtext("av-version")
            wildfireversion = el.findtext("wildfire-version")
               
               
                               
            rows.append({"Hostname": hostname,
                "Serial Number" : serial,
                "Model" : model,
                "Software Version" : swversion,
                "App Version" : appversion,
                "AV Version" : avversion,
                "WildFire Version" : wildfireversion})
 
                   
                               
               
        df = pd.DataFrame(rows, columns=cols)
        df = df.reset_index(drop=True)
        df.to_csv(pan + '-output.csv', index=False)
        df = pd.read_csv(pan + '-output.csv')
        clean_df = df.dropna()
        clean_df.to_csv(pan + '-output-clean.csv', index=False)

               
get_con_devices()


