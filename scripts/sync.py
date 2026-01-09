import requests
import os
import sys
import json

def log(msg):
    print(f"[LOG] {msg}", flush=True)

def error(msg):
    print(f"[ERROR] {msg}", flush=True)
    sys.exit(1)

log("🚀 Script started")

# --- Load environment variables ---
try:
    REDASH_URL = os.environ["REDASH_URL"]
    REDASH_API_KEY = os.environ["REDASH_API_KEY"]
    QUERY_ID = os.environ["QUERY_ID"]
    CLICKUP_TOKEN = os.environ["CLICKUP_TOKEN"]
    CLICKUP_LIST_ID = os.environ["CLICKUP_LIST_ID"]
except KeyError as e:
    error(f"Missing environment variable: {e}")

log("✅ Environment variables loaded")

# --- Fetch Redash data ---
redash_api = f"{REDASH_URL}/api/queries/{QUERY_ID}/results.json?api_key={REDASH_API_KEY}"
log(f"Fetching Redash data from: {redash_api}")

try:
    redash_response = requests.get(redash_api, timeout=30)
    log(f"Redash response status: {redash_response.status_code}")
except Exception as e:
    error(f"Redash API request failed: {e}")

if redash_response.status_code != 200:
    error(f"Redash API returned non-200 response: {redash_response.text}")

try:
    redash_json = redash_response.json()
    rows = redash_json["query_result"]["data"]["rows"]
except Exception as e:
    error(f"Failed to parse Redash response JSON: {e}")

log(f"📊 Redash rows fetched: {len(rows)}")

if not rows:
    log("⚠️ No data returned from Redash — exiting safely")
    sys.exit(0)

# --- ClickUp setup ---
clickup_url = f"https://api.clickup.com/api/v2/list/{CLICKUP_LIST_ID}/task"
headers = {
    "Authorization": CLICKUP_TOKEN,
    "Content-Type": "application/json"
}

log(f"ClickUp task creation URL: {clickup_url}")

# --- Process rows ---
for index, row in enumerate(rows, start=1):
    log(f"➡️ Processing row {index}: {row}")

    metric_name = row.get("metric_name") or row.get("name") or "Unknown Metric"
    metric_value = row.get("metric_value") or row.get("value") or "N/A"

    task_payload = {
        "name": f"Metric Alert: {metric_name}",
        "description": f"Value: {metric_value}",
        "status": "to do"
    }

    log(f"📦 Task payload: {json.dumps(task_payload)}")

    try:
        response = requests.post(
            clickup_url,
            headers=headers,
            json=task_payload,
            timeout=30
        )
    except Exception as e:
        error(f"ClickUp API request failed: {e}")

    log(f"ClickUp response status: {response.status_code}")
    log(f"ClickUp response body: {response.text}")

    if response.status_code not in [200, 201]:
        log("❌ Task creation failed for this row — continuing")
    else:
        log("✅ Task successfully created")

log("🎉 Script completed successfully")
