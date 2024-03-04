import requests
import xml.etree.ElementTree as ET
import getpass
from openpyxl import Workbook

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

def get_users_and_roles(firewall_ip, api_key):
    url = f"https://{firewall_ip}/api/?type=config&action=get&xpath=/config/mgt-config/users"
    headers = {
        'X-PAN-KEY': api_key,
        'Content-Type': 'application/xml'
    }
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        users = {}
        for entry in root.findall(".//entry[phash]"):  # Filter users with phash
            username = entry.get('name')
            roles = [role.text for role in entry.findall("./phash/entry/role")]
            users[username] = roles
        return users
    else:
        print(f"Failed to retrieve users and roles from {firewall_ip}. Status code: {response.status_code}")
        return None

def main():
    wb = Workbook()
    username = input("Enter your firewall username: ")
    password = getpass.getpass("Enter your firewall password: ")

    with open('firewalls.txt', 'r') as file:
        firewalls = file.read().splitlines()

    for firewall_ip in firewalls:
        api_key = generate_api_key(firewall_ip, username, password)
        if api_key:
            users_and_roles = get_users_and_roles(firewall_ip, api_key)
            if users_and_roles:
                ws = wb.create_sheet(title=firewall_ip)
                ws.append(['Username', 'Role'])
                for user, roles in users_and_roles.items():
                    if roles:
                        ws.append([user, ', '.join(roles)])
                    else:
                        ws.append([user, 'None'])
            else:
                print(f"No users found on {firewall_ip}.")
        else:
            print(f"Failed to generate API key for {firewall_ip}.")

    wb.save("firewalls_users_and_roles.xlsx")
    print("Excel file created successfully.")

if __name__ == "__main__":
    main()
