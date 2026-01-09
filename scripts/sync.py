import requests
import os

REDASH_URL = os.environ["REDASH_URL"]
REDASH_API_KEY = os.environ["REDASH_API_KEY"]
QUERY_ID = os.environ["QUERY_ID"]

CLICKUP_TOKEN = os.environ["CLICKUP_TOKEN"]
CLICKUP_LIST_ID = os.environ["CLICKUP_LIST_ID"]

# Fetch Redash data
redash_api = f"{REDASH_URL}/api/queries/{QUERY_ID}/results.json?api_key={REDASH_API_KEY}"
response = requests.get(redash_api)
data = response.json()["query_result"]["data"]["rows"]

# Example: Create one ClickUp task per row
for row in data:
    task_payload = {
        "name": f"Metric Alert: {row['metric_name']}",
        "description": f"Value: {row['metric_value']}",
        "status": "to do"
    }

    clickup_url = f"https://api.clickup.com/api/v2/list/{CLICKUP_LIST_ID}/task"
    headers = {
        "Authorization": CLICKUP_TOKEN,
        "Content-Type": "application/json"
    }

    requests.post(clickup_url, json=task_payload, headers=headers)
