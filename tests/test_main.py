from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_public_articles():
    assert client.get("/articles/").status_code == 200

def test_authenticated_flow():
    user = {"email": "user@test.com", "password": "password123"}
    client.post("/users/", json=user)
    
    login = client.post("/login", data={"username": user["email"], "password": user["password"]})
    assert login.status_code == 200
    
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    article = {"title": "Simple Title", "content": "Short and concise article content."}
    response = client.post("/articles/", json=article, headers=headers)
    
    assert response.status_code == 201


def test_duplicate_user():
    user = {"email": "duplicate@test.com", "password": "password123"}
    client.post("/users/", json=user)
    response = client.post("/users/", json=user)
    assert response.status_code == 400

def test_invalid_login():
    response = client.post("/login", data={"username": "nonexistent@test.com", "password": "wrong"})
    assert response.status_code == 400

def test_unauthorized_article_creation():
    article = {"title": "Test", "content": "Test content"}
    response = client.post("/articles/", json=article)
    assert response.status_code == 401

def test_bulk_import():
    user = {"email": "importer@test.com", "password": "password123"}
    client.post("/users/", json=user)
    login = client.post("/login", data={"username": user["email"], "password": user["password"]})
    token = login.json()["access_token"]
    
    import_data = {
        "articles": [
            {"title": "Import 1", "content": "Content 1"},
            {"title": "Import 2", "content": "Content 2"}
        ]
    }
    response = client.post("/articles/import", json=import_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert "Successfully imported 2 articles" in response.json()["message"]