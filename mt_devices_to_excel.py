import os
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from concurrent.futures import ThreadPoolExecutor

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
def send_email(sender_email, receiver_email, smtp_server, smtp_port):
    subject = "Firewall Baseline Report"
    body = "Please find the attached firewall baseline xlsx file. Showing the firewalls and their software versions."

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(receiver_email)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    filename = "firewall_baseline.xlsx"
    attachment = open(filename, "rb")

    part = MIMEBase("application", "octet-stream")
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename= {filename}")

    msg.attach(part)
    text = msg.as_string()

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.sendmail(sender_email, receiver_email, text)
    server.quit()
    
def fetch_firewall_data(pan, username, password):
    rest_url = "/api/?type=op&cmd=<show><devices><connected></connected></devices></show>"
    api_key = generate_api_key(pan, username, password)
    if api_key:
        url = "https://" + pan + rest_url + "&key=" + api_key
        resp = requests.get(url, verify=False)
        xmldata = ET.fromstring(resp.content)

        rows = []
        for el in xmldata.iter('entry'):
            rows.append({
                "Hostname": el.findtext("hostname"),
                "Serial Number": el.findtext("serial"),
                "Model": el.findtext("model"),
                "Software Version": el.findtext("sw-version"),
                "App Version": el.findtext("app-version"),
                "AV Version": el.findtext("av-version"),
                "WildFire Version": el.findtext("wildfire-version")
            })
        return rows
    else:
        return []

def get_con_devices():
    username = ""
    password = ""
    sender_email = "Perimeter_Firewall_Engineering@optum.com"
    receiver_email = ["evan_snell@optum.com", "taylor_kerber@optum.com", "phil@optum.com"]
    smtp_server = "mailo2.uhc.com"
    smtp_port = 25

    with open('panoramas.txt', 'r', encoding="utf-8") as file:
        panoramas = file.read().splitlines()

    all_devices = []
    with ThreadPoolExecutor(max_workers=11) as executor:
        results = executor.map(lambda pan: fetch_firewall_data(pan, username, password), panoramas)

    for result in results:
        all_devices.extend(result)

    cols = ["Hostname", "Serial Number", "Model", "Software Version", "App Version", "AV Version", "WildFire Version"]
    df = pd.DataFrame(all_devices, columns=cols)
    df.to_excel('firewall_dirty.xlsx', index=False)
    df = pd.read_excel('firewall_dirty.xlsx')
    clean_df = df.dropna()
    clean_df.to_excel('firewall_baseline.xlsx', index=False)

    send_email(sender_email, receiver_email, smtp_server, smtp_port)
    
    os.remove('firewall_dirty.xlsx')

get_con_devices()
