import requests
import pytest

def test_register():
    response = requests.post("http://127.0.0.1:5000/register", data={"first_name": "Sarim", "last_name": "Sikander", "email": "sarim24@gmail.com", "password": "sarim123"})
    assert response.text in ["User created successfully","There already is a user by that name"]
    
def test_login():
    email = "sarim24@gmail.com"
    response = requests.post("http://127.0.0.1:5000/login", data={"email": email, "password": "sarim123"})
    assert response.status_code == 200
    
def test_logout():
    response = requests.get("http://127.0.0.1:5000/logout")
    assert response.status_code == 200