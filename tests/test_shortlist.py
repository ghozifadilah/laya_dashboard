def test_shortlist(client):
    payload = {
        "state": "The customer is asking for technical assistance with Python API integration errors.",
        "instructions": "Which team should be assigned?",
        "criteria": {
            "billing_disputes": "invoice and payment disputes",
            "account_cancellation": "cancellations and account closures",
            "python_sdk_support": "python integration, sdk errors, and backend development",
            "sales_enterprise": "enterprise contracts and volume pricing",
            "hr_careers": "job applications and hiring",
            "hardware_repair": "device repairs and physical equipment"
        },
        "k": 3
    }
    response = client.post("/api/v1/shortlist", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "selected_choice" in data
    assert "shortlisted_candidates" in data
    assert len(data["shortlisted_candidates"]) <= 3
