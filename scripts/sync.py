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

# --- Fetch Redash query results (cached) ---
redash_api = (
    f"{REDASH_URL}/api/queries/{QUERY_ID}/results.json"
    f"?api_key={REDASH_API_KEY}"
)

log("📡 Fetching Redash query results")

try:
    response = requests.get(redash_api, timeout=30)
    log(f"Redash response status: {response.status_code}")
except Exception as e:
    error(f"Redash API request failed: {e}")

if response.status_code != 200:
    error(f"Redash API error: {response.text}")

try:
    data = response.json()
    rows = data["query_result"]["data"]["rows"]
except Exception as e:
    error(f"Failed parsing Redash response: {e}")

log(f"📊 Rows fetched: {len(rows)}")

# Expecting a single-row result with `ids`
ids = None
if rows and isinstance(rows, list):
    ids = rows[0].get("ids")

if not ids:
    log("⚠️ No new merchant records found. Skipping execution.")
    sys.exit(0)

log(f"✅ New merchant IDs detected: {ids}")




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
