# Import requests module
import requests
from getpass import getpass
import xml.etree.ElementTree as XML

# Define the Panorama's hostname or IP address
panorama = "https://10.151.151.252"

# Prompt username and password
user = input("User:")
password = getpass(prompt='Pass:')

# Define the URL parameters for the keygen request
params = {
    "type": "keygen",
    "user": user,
    "password": password
}

# Disable insecure warning in output
requests.packages.urllib3.disable_warnings()
# Make the API request
reply = requests.post(panorama + "/api/", params=params, verify=False)

# Check response status
if reply.status_code == 200 and "<response status = 'success'>" in reply.text:
# Extract the API key from the reply text
    xml_response = XML.fromstring(reply.text)

# Extract key from xml reply
    api_key = xml_response.find('.//key').text
# Print API key
    print("API key: " + api_key)
else:
# Print the error
    print("Error: " + reply.text)