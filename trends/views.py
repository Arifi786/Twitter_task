
import os
import subprocess

import datetime

from django.http import JsonResponse
from django.shortcuts import render
from pymongo import MongoClient
from rest_framework.utils import json


def index(request):
    return render(request, 'index.html')



# # ProxyMesh credentials (you can fetch these from your environment variables or config file)
# PROXY_USERNAME = 'your_proxy_username'  # Replace with your ProxyMesh username
# PROXY_PASSWORD = 'your_proxy_password'  # Replace with your ProxyMesh password
# PROXY_HOST = 'proxy.proxyMesh.com'  # ProxyMesh host
# PROXY_PORT = '31280'  # ProxyMesh port (typically 31280, unless specified otherwise)
#
# def get_proxy():
#     # Construct the ProxyMesh URL with your username and password
#     return f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}"


# View to trigger the Selenium script
def run_selenium_script(request):
    print("Selenium script")
    try:
        script_path = os.path.join(os.path.dirname(__file__), 'fetch_trends.py')


        result = subprocess.run(
            ['python3', script_path],
            capture_output=True,
            text=True,
            timeout=60  # Timeout in seconds
        )
        if result.returncode == 0:
            client = MongoClient("mongodb://localhost:27017/")
            db = client["twitter_trends"]
            collection = db["trends"]
            print("here")
            # Fetch the latest trends from MongoDB
            latest_trends = collection.find().sort('count', -1).limit(1) # Sorting by "end_time" descending
            end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(latest_trends)
            if latest_trends:

                trends= latest_trends[0].get("trends", [])
                top_five_trends = trends[:5]  # Get the top 5 trends
                latest_trends_doc = list(latest_trends)[0] if latest_trends else None
                ip_address = latest_trends_doc.get("ip_address", "Unknown IP")

                # Now, create the WebDriver with ProxyMesh proxy for each request
                # options = Options()
                # options.add_argument(f'--proxy-server={get_proxy()}')  # Set ProxyMesh as the proxy

                # Initialize the WebDriver with the specified proxy settings
                # driver = webdriver.Chrome(options=options)

                trend_json = {
                    "_id": latest_trends_doc["_id"],
                    **{f"trend{i + 1}": trend for i, trend in enumerate(top_five_trends)}
                }

                # Convert trend_json to a JSON formatted string with indentation
                formatted_record = json.dumps(trend_json, indent=4)
                # Pass the top 5 trends to the template for rendering
                return render(request, 'top_trends.html', {
                    'trends': top_five_trends, 'end_time': end_time, 'client_ip': ip_address, 'trendj': formatted_record   # Pass the trends to the template
                })
            else:
                # If no trends are found, render a page with an error message
                return render(request, 'top_trends.html', {
                    'error': "No trends found."  # Error message if no trends are available
                })

        else:
            return JsonResponse({'status': 'error', 'message': result.stderr})
    except subprocess.TimeoutExpired:
        return JsonResponse({'status': 'error', 'message': 'Script timed out.'})

#
