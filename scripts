import requests
import os

REDASH_URL = os.environ["https://reports.snapmint.com"]
REDASH_API_KEY = os.environ["xbV5CDo1VQCNvmaeSs7tUNTWYLfeoVsRDAMuOQI6"]
QUERY_ID = os.environ["14581"]

CLICKUP_TOKEN = os.environ["9I9UBYDQ12D8XEJXW0NSSCVE0SXLDFZA879H9PZ9XDA7QS6XFV8R79HE8X032AI1"]
CLICKUP_LIST_ID = os.environ["901412176234"]

# Fetch Redash data
redash_api = f"https://reports.snapmint.com/api/queries/14581/results.json?api_key=xbV5CDo1VQCNvmaeSs7tUNTWYLfeoVsRDAMuOQI6"
response = requests.get(redash_api)
data = response.json()["query_result"]["data"]["rows"]

# Example: Create one ClickUp task per row
for row in data:
    task_payload = {
        "name": f"Metric Alert: {row['Add Unleash MID']}",
        "description": f"Value: {row['id']}",
        "status": "to do"
    }

    clickup_url = f"https://api.clickup.com"
    headers = {
        "Authorization": 9I9UBYDQ12D8XEJXW0NSSCVE0SXLDFZA879H9PZ9XDA7QS6XFV8R79HE8X032AI1,
        "Content-Type": "application/json"
    }

    requests.post(clickup_url, json=task_payload, headers=headers)

