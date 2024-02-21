# Import the requests library
import requests

# Define the URL, username, and password for the firewall or Panorama
url = "https://firewall/api/"
user = "admin"
password = "admin"

# Make a POST request to get the API key
response = requests.post(url, params={"type": "keygen", "user": user, "password": password})

# Parse the XML response and extract the key element
key = response.xml.find("result/key").text

# Print the API key
print("The API key is:", key)