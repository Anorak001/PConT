import requests
import json

# Define the base URL for the API
base_url = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_format=protocolipport&format=text"

# Make the request to the API and get the response
response = requests.get(base_url)

# Counter to check for success of the resposnse
if response.status_code == 200:
    # Parse the JSON response
    json_response = json.loads(response.text)

    # write all the proxies that have been acquired using post into a file named "free_proxies.txt"
    with open('free_proxies.txt', 'w') as f:
        for item in json_response:
            f.write(str(item) + "\n")

else:
    print("Error: Unable to access the API. Response status code:", response.status_code)
