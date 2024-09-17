import requests

# base URL for the API
base_url = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_format=protocolipport&format=text"

# Make the request to the API and get the response
response = requests.get(base_url)

# Check if the request was successful
if response.status_code == 200:
    # Check if the content is as expected (not empty)
    if response.text.strip():  # Ensure the content is not empty
        # Write all the proxies that have been acquired into a file named "free_proxies.txt"
        with open('free_proxies.txt', 'w') as f:
            f.write(response.text)
else:
   
    pass  #  log or handle it in a way suitable for integration
