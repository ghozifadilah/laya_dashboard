def test_create_and_list_custom_workflow(client):
    payload = {
        "name": "ecommerce_fraud_test",
        "title": "E-Commerce Fraud Test",
        "description": "Workflow deteksi penipuan transaksi",
        "model": "auto",
        "example_state": {
            "order_id": "ORD-001",
            "amount": 10000000,
            "card_country": "ID"
        },
        "questions": {
            "action": {
                "type": "choice",
                "instructions": "Apa tindakan order?",
                "criteria": {
                    "approve": "transaksi aman",
                    "reject": "penipuan"
                }
            },
            "is_fraud": {
                "type": "noul",
                "instructions": "Apakah ada indikasi fraud?"
            }
        }
    }

    # 1. Create
    res = client.post("/api/v1/workflows", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "ecommerce_fraud_test"
    assert data["is_custom"] is True

    # 2. List
    list_res = client.get("/api/v1/workflows")
    assert list_res.status_code == 200
    names = [w["name"] for w in list_res.json()["workflows"]]
    assert "ecommerce_fraud_test" in names

    # 3. Test executing it via preset in predict endpoint
    pred_res = client.post("/api/v1/predict", json={
        "state": "Pembelian 5 gadget kartu baru",
        "preset": "ecommerce_fraud_test"
    })
    assert pred_res.status_code == 200
    assert pred_res.json()["success"] is True
    assert "action" in pred_res.json()["answers"]

    # 4. Delete
    del_res = client.delete("/api/v1/workflows/ecommerce_fraud_test")
    assert del_res.status_code == 200
