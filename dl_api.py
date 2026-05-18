# Calls the DeliberateLab REST API to create a dedicated 2-person cohort
# for a matched pair. Returns the participant join URL.

import requests
from settings import DL_CONFIG


def create_dl_cohort(condition: str, seed_message: str = None) -> str:
    experiment_id  = DL_CONFIG['EXPERIMENTS'][condition]
    api_url        = DL_CONFIG['API_URL']
    frontend_url   = DL_CONFIG['FRONTEND_URL']
    api_key        = DL_CONFIG['API_KEY']

    # DL not yet configured — return a stub URL so matching still works locally
    if not api_url or not api_key:
        print(f"[dl_api] DL not configured — using placeholder URL for condition '{condition}'")
        return f"https://placeholder.deliberatelab.example/condition/{condition}"

    url = f"{api_url}/api/v1/experiments/{experiment_id}/cohorts"
    print(f"[dl_api] POST {url}")

    body = {
        "name": f"pair_{condition}",
        "participantConfig": {
            "minParticipantsPerCohort": 2,
            "maxParticipantsPerCohort": 2,
        },
    }
    if seed_message:
        body["seedMessage"] = seed_message

    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
        json=body,
        timeout=10,
    )

    print(f"[dl_api] status={response.status_code} body={response.text[:500]!r}")
    response.raise_for_status()
    cohort_id = response.json()["cohort"]["id"]
    return f"{frontend_url}/#/e/{experiment_id}/c/{cohort_id}"
