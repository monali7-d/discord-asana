import os
import traceback
import requests

ASANA_API_BASE = "https://app.asana.com/api/1.0"

# Optional: comma-separated Asana tag GIDs in env
ASANA_TAG_GIDS = os.getenv("ASANA_TAG_GIDS", "")  # e.g., "120000000000001,120000000000002"
# Optional: custom field GID to store the Discord Message ID
ASANA_DISCORD_MSG_ID_FIELD_GID = os.getenv("ASANA_DISCORD_MSG_ID_FIELD_GID", "")


def _build_task_payload(event, asana_project_gid):
    title = (event.get("content") or "").strip()[:120] or f"Discord message {event['message_id']}"
    description = (
        f"Author: {event.get('author')}\n\n"
        f"Message: {event.get('content')}\n\n"
        f"View on Discord: {event.get('permalink')}\n"
    )

    data = {
        "name": title,
        "notes": description,
        "projects": [asana_project_gid],
    }

    # Tags: expect tag GIDs if provided
    tag_gids = [t.strip() for t in ASANA_TAG_GIDS.split(",") if t.strip()]
    if tag_gids:
        data["tags"] = tag_gids

    # Custom field: set Discord message ID if a field gid is provided
    if ASANA_DISCORD_MSG_ID_FIELD_GID:
        data["custom_fields"] = {ASANA_DISCORD_MSG_ID_FIELD_GID: event.get("message_id")}

    return data


async def create_asana_task(event, asana_pat, asana_project_gid):
    if not asana_pat or not asana_project_gid:
        print("ERROR: ASANA_PAT or ASANA_PROJECT_GID is missing. Cannot create Asana task.")
        return

    try:
        payload = {"data": _build_task_payload(event, asana_project_gid)}
        print(f"Task data to send: {payload}")

        headers = {
            "Authorization": f"Bearer {asana_pat}",
            "Content-Type": "application/json",
        }

        resp = requests.post(f"{ASANA_API_BASE}/tasks", json=payload, headers=headers, timeout=20)
        if resp.status_code >= 200 and resp.status_code < 300:
            body = resp.json()
            gid = body.get("data", {}).get("gid")
            print(f"Created Asana task: {gid}")
        else:
            print(f"Failed to create Asana task: HTTP {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Failed to create Asana task: {e}")
        traceback.print_exc()
