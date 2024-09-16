import requests

# Define the base URL for the API
base_url = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_format=protocolipport&format=text"

# Make the request to the API and get the response
response = requests.get(base_url)

# Check if the request was successful
if response.status_code == 200:
    print("Request successful. Status code:", response.status_code)

    # Print out the response content to verify what is being returned
    print("Response Content:\n", response.text)

    # Check if the content is as expected (not empty)
    if response.text.strip():  # Ensure the content is not empty
        # Write all the proxies that have been acquired into a file named "free_proxies.txt"
        with open('free_proxies.txt', 'w') as f:
            f.write(response.text)
        print("Proxies have been written to 'free_proxies.txt'")
    else:
        print("Warning: The response content is empty.")
else:
    print("Error: Unable to access the API. Response status code:", response.status_code)
