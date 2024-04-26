import threading
import requests
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

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

def fetch_firewall_data(panorama, username, password, all_devices, lock):
    api_key = generate_api_key(panorama, username, password)
    if api_key:
        rest_url = f"/api/?type=op&cmd=<show><devices><connected></connected></devices></show>&key={api_key}"
        url = f"https://{panorama}{rest_url}"
        print(f"Fetching data from: {panorama}")

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
                         "Serial Number": serial,
                         "Model": model,
                         "Software Version": swversion,
                         "App Version": appversion,
                         "AV Version": avversion,
                         "WildFire Version": wildfireversion})

        with lock:
            all_devices.extend(rows)

def get_con_devices_threaded():
    username = ""
    password = ""
    all_devices = []  # List to accumulate data from all panoramas
    lock = threading.Lock()

    with open('panoramas.txt', 'r', encoding="utf-8") as file:
        panoramas = file.read().splitlines()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_firewall_data, pan, username, password, all_devices, lock) for pan in panoramas]
        # Wait for all threads to complete
        for future in futures:
            future.result()

    # Further processing, saving to Excel, sending emails, etc., would follow here

# Example call (commented out for now)
# get_con_devices_threaded()
