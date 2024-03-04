import csv
import requests
import xml.etree.ElementTree as ET

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
        for entry in root.findall(".//entry"):
            username = entry.get('name')
            roles = [role.text for role in entry.findall("./phash/entry/role")]
            users[username] = roles
        return users
    else:
        print(f"Failed to retrieve users and roles from {firewall_ip}. Status code: {response.status_code}")
        return None

def main():
    with open('firewalls.txt', 'r') as file:
        firewalls = file.read().splitlines()

    api_key = 'LUFRPT1SblppdmMraWNjZzhLUDJsM0tBK1ZHZk83eGc9UlkvSDBiUVI1SmhGNG14YktVZHNSZjRCdHBweURxanZnUUthb2xVM0ZqUCtYYXJIM01Ca2V1NUJLb1A5Q0RiNQ=='

    for firewall_ip in firewalls:
        users_and_roles = get_users_and_roles(firewall_ip, api_key)
        if users_and_roles:
            filename = f"{firewall_ip}_users_and_roles.csv"
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['Username', 'Role']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for user, roles in users_and_roles.items():
                    if roles:
                        writer.writerow({'Username': user, 'Role': ', '.join(roles)})
                    else:
                        writer.writerow({'Username': user, 'Role': 'None'})
            print(f"User and role information for {firewall_ip} written to {filename}")
        else:
            print(f"No users found on {firewall_ip}.")

if __name__ == "__main__":
    main()
