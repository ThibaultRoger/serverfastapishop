def test_liveness(client):
    body = client.get("/health").json()
    assert body["status"] == "ok" and {"version", "commit"} <= set(body)


def test_readiness(client):
    assert client.get("/ready").status_code == 200


def test_openapi_is_valid(client):
    assert client.get("/openapi.json").status_code == 200
