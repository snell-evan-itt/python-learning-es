import getpass
import requests
import xml.etree.ElementTree as ET
import pandas as pd

requests.packages.urllib3.disable_warnings()

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
    username = ""
    password = ""
   
    with open('panoramas.txt','r', encoding="utf-8") as file:
        panoramas = file.read().splitlines()
   
    rest_url = "/api/?type=op&cmd=<show><devices><connected></connected></devices></show>"
    
    all_devices = []  # List to accumulate data from all panoramas
    
    for pan in panoramas:
        api_key = generate_api_key(pan, username, password)
        url = "https://" + pan + rest_url + "&key=" + api_key
        print(pan)
       
        resp = requests.get(url, verify=False)
        xmldata = ET.fromstring(resp.content)
           
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
 
        all_devices.extend(rows)
 
    cols = ["Hostname", "Serial Number", "Model", "Software Version", "App Version", "AV Version", "WildFire Version"]
    df = pd.DataFrame(all_devices, columns=cols)
    df.to_csv('firewall_dirty.csv', index=False)
    df = pd.read_csv('firewall_dirty.csv')
    clean_df = df.dropna()
    clean_df.to_csv('firewall_baseline.csv', index=False)

get_con_devices()
