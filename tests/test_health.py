def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "device" in data


def test_readiness(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["ready"] is True


def test_liveness(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["live"] is True
