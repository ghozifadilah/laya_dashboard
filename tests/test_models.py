def test_list_models(client):
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) >= 3
    model_names = [m["name"] for m in data["models"]]
    assert "english" in model_names
    assert "multilingual" in model_names
    assert "typed-decisions" in model_names


def test_inspect_route_english(client):
    payload = {
        "state": "The user is asking how to change their payment password."
    }
    response = client.post("/api/v1/router/inspect", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "english"
    assert "reason" in data


def test_inspect_route_multilingual(client):
    payload = {
        "state": "मुझसे दो बार शुल्क लिया गया, कृपया पैसे वापस करें।"
    }
    response = client.post("/api/v1/router/inspect", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "multilingual"
    assert "devanagari" in data["reason"] or "script" in data["reason"]
