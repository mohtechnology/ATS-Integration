import os
import json
import requests

ATS_KEY = os.getenv("ATS_API_KEY", "")
ATS_URL = os.getenv("ATS_BASE_URL", "")

def get_headers():
    # Only return Authorization header if key exists
    if ATS_KEY.strip():
        return {"Authorization": f"Bearer {ATS_KEY}"}
    return {}

def get_jobs(event, context):
    url = f"{ATS_URL}/jobs"
    headers = get_headers()

    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return {
            "statusCode": res.status_code,
            "body": json.dumps({"error": "Failed to fetch jobs"})
        }

    data = res.json()

    jobs = [
        {
            "id": j.get("id"),
            "title": j.get("title"),
            "location": j.get("location"),
            "status": j.get("status"),
            "external_url": j.get("external_url")
        }
        for j in data.get("results", [])
    ]

    return {
        "statusCode": 200,
        "body": json.dumps(jobs)
    }


def create_candidate(event, context):
    body = json.loads(event.get("body", "{}"))

    payload = {
        "name": body.get("name"),
        "email": body.get("email"),
        "phone": body.get("phone"),
        "resume_url": body.get("resume_url")
    }

    headers = get_headers()

    create_url = f"{ATS_URL}/candidates"
    candidate_res = requests.post(create_url, json=payload, headers=headers)

    if candidate_res.status_code not in [200, 201]:
        return {
            "statusCode": candidate_res.status_code,
            "body": json.dumps({"error": "Candidate creation failed"})
        }

    cand_id = candidate_res.json().get("id")

    # Now attach candidate to job
    app_payload = {"job_id": body.get("job_id")}
    app_url = f"{ATS_URL}/applications"

    app_res = requests.post(app_url, json=app_payload, headers=headers)

    if app_res.status_code not in [200, 201]:
        return {
            "statusCode": app_res.status_code,
            "body": json.dumps({"error": "Failed to attach candidate to job"})
        }

    return {
        "statusCode": 201,
        "body": json.dumps({"message": "Candidate created and attached"})
    }


def get_applications(event, context):
    job_id = event.get("queryStringParameters", {}).get("job_id")

    if not job_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing job_id"})
        }

    url = f"{ATS_URL}/applications?job_id={job_id}"
    headers = get_headers()

    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return {
            "statusCode": res.status_code,
            "body": json.dumps({"error": "Failed to fetch applications"})
        }

    data = res.json()

    apps = [
        {
            "id": a.get("id"),
            "candidate_name": a.get("candidate_name"),
            "email": a.get("email"),
            "status": a.get("status")
        }
        for a in data.get("results", [])
    ]

    return {
        "statusCode": 200,
        "body": json.dumps(apps)
    }
