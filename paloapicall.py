# Import packages 
import requests
from getpass import getpass

# Define the Panorama's hostname or IP address
panorama = "https://10.151.151.252"

# Prompt username and password
user = input("User:")
password = getpass(prompt='Pass:')

# Define paramaters 
params = {
    "type": "keygen",
    "user": user,
    "password": password
}

# Disable insecure warning in output
requests.packages.urllib3.disable_warnings()
# Make the API request
response = requests.post(panorama + "/api/", params=params, verify=False)

# Check response status
if response.status_code == 200 and "<response status = \'success\'>" in response.text:
    # Extract the API key
    api_key = response.text.split("<key>")[1].split("</key>")[0]
    # Print API key
    print("API key: " + api_key)
else:
    # Print the error
    print("Error: " + response.text)