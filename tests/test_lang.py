def test_detect_english(client):
    payload = {"text": "Hello, I would like to request a refund for order #1234"}
    response = client.post("/api/v1/lang/detect", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "en"
    assert data["script"] == "latin"
    assert data["is_english"] is True
    assert data["recommended_model"] == "english"


def test_detect_hindi(client):
    payload = {"text": "मुझसे दो बार शुल्क लिया गया, कृपया पैसे वापस करें।"}
    response = client.post("/api/v1/lang/detect", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["script"] == "devanagari"
    assert data["is_english"] is False
    assert data["recommended_model"] == "multilingual"
