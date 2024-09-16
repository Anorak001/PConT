import requests

# Define the base URL for the API
base_url = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_format=protocolipport&format=text"

# Make the request to the API and get the response
response = requests.get(base_url)

# Counter to check for success of the response
if response.status_code == 200:
    # Write all the proxies that have been acquired into a file named "free_proxies.txt"
    with open('free_proxies.txt', 'w') as f:
        f.write(response.text)  # Write the raw response text directly into the file

else:
    print("Error: Unable to access the API. Response status code:", response.status_code)
