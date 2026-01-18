import requests
import os
import sys
from datetime import datetime

logs = []

def log(msg):
    line = f"[LOG] {msg}"
    print(line, flush=True)
    logs.append(line)

def error(msg):
    line = f"[ERROR] {msg}"
    print(line, flush=True)
    logs.append(line)
    send_slack("❌ Redash query run FAILED", "\n".join(logs))
    sys.exit(1)

def send_slack(title, message):
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook:
        print("[WARN] Slack webhook not configured", flush=True)
        return

    payload = {
        "text": f"*{title}*\n```{message[-3500:]}```"
    }

    try:
        requests.post(webhook, json=payload, timeout=10)
    except Exception as e:
        print(f"[WARN] Failed to send Slack message: {e}", flush=True)

log("🚀 Script started")

# --- Load environment variables ---
try:
    REDASH_URL = os.environ["REDASH_URL"]
    REDASH_API_KEY = os.environ["REDASH_API_KEY"]
    QUERY_ID = os.environ["QUERY_ID"]
except KeyError as e:
    error(f"Missing environment variable: {e}")

log("✅ Environment variables loaded")

# --- Fetch Redash data ---

# --- Trigger Redash refresh ---
refresh_url = f"{REDASH_URL}/api/queries/{QUERY_ID}/refresh"
headers = {"Authorization": f"Key {REDASH_API_KEY}"}

log("Triggering Redash query refresh")

try:
    refresh_resp = requests.post(refresh_url, headers=headers, timeout=30)
    refresh_resp.raise_for_status()
except Exception as e:
    error(f"Failed to refresh Redash query: {e}")

job = refresh_resp.json()["job"]
job_id = job["id"]

log(f"Refresh job started: {job_id}")

# --- Poll for result ---
result = None
for _ in range(10):
    job_status = requests.get(
        f"{REDASH_URL}/api/jobs/{job_id}",
        headers=headers,
        timeout=10
    ).json()

    if job_status["job"]["status"] == 3:  # SUCCESS
        result = job_status["job"]["query_result_id"]
        break

    log("Waiting for query to finish...")
    time.sleep(5)

if not result:
    error("Redash query did not finish in time")

# --- Fetch latest results ---
result_url = f"{REDASH_URL}/api/query_results/{result}.json"
log("Fetching fresh Redash results")

rows = requests.get(result_url, headers=headers, timeout=30) \
               .json()["query_result"]["data"]["rows"]


# --- Build Slack message body ---
message_lines = []
for idx, row in enumerate(rows, start=1):
    message_lines.append(f"{idx}. {row}")

rows_text = "\n".join(message_lines)

summary = (
    f"Run Time: {datetime.utcnow().isoformat()} UTC\n"
    f"Rows fetched: {len(rows)}\n\n"
    f"Data:\n{rows_text}"
)

log("🎉 Script completed")

send_slack(
    "@sathwik.rai @Rahul Manglik Please add these below MIDs for checkout 3.0",
    summary
)
