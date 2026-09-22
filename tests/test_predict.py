def test_predict_with_custom_questions(client):
    payload = {
        "state": {
            "from": "user@acme.com",
            "subject": "Refund requested for invoice #1024",
            "body": "I was billed twice. Please issue a refund today or I cancel my subscription."
        },
        "questions": {
            "department": {
                "type": "choice",
                "instructions": "Which department should handle this?",
                "criteria": {
                    "billing": "invoices, payments, refunds",
                    "technical": "bugs, outages",
                    "sales": "new deals"
                }
            },
            "urgency": {
                "type": "score",
                "instructions": "How urgent is this?",
                "criteria": ["low", "medium", "high", "critical"]
            },
            "churn_risk": {
                "type": "noul",
                "instructions": "Does the user threaten to cancel?"
            }
        }
    }

    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "answers" in data
    assert "department" in data["answers"]
    assert "urgency" in data["answers"]
    assert "churn_risk" in data["answers"]
    assert "routing" in data
    assert "latency_ms" in data


def test_predict_with_preset(client):
    payload = {
        "state": "The server is returning 500 internal server error on checkout",
        "preset": "triage"
    }

    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "intent" in data["answers"]
    assert "is_urgent" in data["answers"]


def test_batch_predict(client):
    payload = {
        "items": [
            "Please refund my money for duplicate order",
            "How do I reset my password?"
        ],
        "preset": "triage"
    }

    response = client.post("/api/v1/predict/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total_items"] == 2
    assert len(data["results"]) == 2
