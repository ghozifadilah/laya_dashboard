def test_email_clean(client):
    payload = {
        "body": "Hi team,\n\nPlease process this request.\n\n--\nBest regards,\nJohn Doe\nAcme Corp\nConfidentiality Notice: This message is intended only for the use..."
    }
    response = client.post("/api/v1/email/clean", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "cleaned_text" in data
    assert data["cleaned_length"] <= data["original_length"]


def test_email_state(client):
    payload = {
        "subject": "Urgent outage in production",
        "body": "API returns 500 error",
        "sender": "lead-dev@company.com"
    }
    response = client.post("/api/v1/email/state", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "state" in data
    assert data["state"]["subject"] == "Urgent outage in production"


def test_email_triage(client):
    payload = {
        "subject": "Need invoice refund for duplicate billing",
        "body": "Hi, we noticed two identical transactions on our credit card statement.",
        "sender": "client@enterprise.com"
    }
    response = client.post("/api/v1/email/triage", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "summary" in data
    assert "category" in data["summary"]
