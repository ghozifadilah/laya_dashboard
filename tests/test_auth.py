def test_login_success(client):
    payload = {"username": "admin", "password": "admin123"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "token" in data
    assert data["user"]["username"] == "admin"


def test_login_failure(client):
    payload = {"username": "admin", "password": "wrongpassword"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401


def test_get_me_and_change_password(client):
    # 1. Login
    login_res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get me
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["username"] == "admin"

    # 3. Change password to new password
    chpass_res = client.post(
        "/api/v1/auth/change-password",
        json={"old_password": "admin123", "new_password": "newadminpassword456"},
        headers=headers,
    )
    assert chpass_res.status_code == 200

    # 4. Verify login with new password
    login_new = client.post("/api/v1/auth/login", json={"username": "admin", "password": "newadminpassword456"})
    assert login_new.status_code == 200
    new_token = login_new.json()["token"]

    # 5. Restore password back to admin123 for default test suite
    client.post(
        "/api/v1/auth/change-password",
        json={"old_password": "newadminpassword456", "new_password": "admin123"},
        headers={"Authorization": f"Bearer {new_token}"},
    )
