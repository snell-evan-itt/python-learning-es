import requests
import xml.etree.ElementTree as ET
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

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
    subject = "Firewall Baseline CSV"
    body = "Please find the attached firewall baseline CSV file."

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    filename = "firewall_baseline.csv"
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

def get_con_devices():
    username = ""
    password = ""
    sender_email = "your_email@example.com"  # Sender's email address
    receiver_email = "recipient@example.com"  # Receiver's email address
    smtp_server = "smtp.example.com"  # SMTP server address
    smtp_port = 25  # SMTP port number

    with open('panoramas.txt', 'r', encoding="utf-8") as file:
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
                         "Serial Number": serial,
                         "Model": model,
                         "Software Version": swversion,
                         "App Version": appversion,
                         "AV Version": avversion,
                         "WildFire Version": wildfireversion})

        all_devices.extend(rows)

    cols = ["Hostname", "Serial Number", "Model", "Software Version", "App Version", "AV Version", "WildFire Version"]
    df = pd.DataFrame(all_devices, columns=cols)
    df.to_csv('firewall_dirty.csv', index=False)
    df = pd.read_csv('firewall_dirty.csv')
    clean_df = df.dropna()
    clean_df.to_csv('firewall_baseline.csv', index=False)

    send_email(sender_email, receiver_email, smtp_server, smtp_port)

get_con_devices()
