def test_api_key_lifecycle_and_protection(client):
    # 1. Login to obtain user token for management
    login_res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert login_res.status_code == 200
    user_token = login_res.json()["token"]
    mgmt_headers = {"Authorization": f"Bearer {user_token}"}

    # 2. Enable protection
    client.post("/api/v1/api-keys/toggle-protection", json={"enabled": True}, headers=mgmt_headers)

    # 3. Generate new API Key
    gen_res = client.post("/api/v1/api-keys", json={"name": "Test Integration Key"}, headers=mgmt_headers)
    assert gen_res.status_code == 201
    key_data = gen_res.json()
    api_token = key_data["token"]
    key_id = key_data["id"]
    assert api_token.startswith("laya_live_")

    # 4. List keys
    list_res = client.get("/api/v1/api-keys", headers=mgmt_headers)
    assert list_res.status_code == 200
    assert list_res.json()["protection_enabled"] is True
    ids = [k["id"] for k in list_res.json()["keys"]]
    assert key_id in ids

    # 5. Call predict endpoint with valid API Key header
    pred_res = client.post(
        "/api/v1/predict",
        json={"state": "Test inquiry", "preset": "triage"},
        headers={"X-API-Key": api_token},
    )
    assert pred_res.status_code == 200
    assert pred_res.json()["success"] is True

    # 6. Call predict endpoint without any key when protection is enabled -> 401
    unauth_res = client.post(
        "/api/v1/predict",
        json={"state": "Test inquiry", "preset": "triage"},
    )
    assert unauth_res.status_code == 401

    # 7. Call predict endpoint with invalid fake key -> 403
    forbidden_res = client.post(
        "/api/v1/predict",
        json={"state": "Test inquiry", "preset": "triage"},
        headers={"X-API-Key": "laya_live_fake_invalid_token"},
    )
    assert forbidden_res.status_code == 403

    # 8. Delete / Revoke API Key
    del_res = client.delete(f"/api/v1/api-keys/{key_id}", headers=mgmt_headers)
    assert del_res.status_code == 200

    # 9. Call with revoked key -> 403
    revoked_res = client.post(
        "/api/v1/predict",
        json={"state": "Test inquiry", "preset": "triage"},
        headers={"X-API-Key": api_token},
    )
    assert revoked_res.status_code == 403
