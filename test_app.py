import pytest
import json
import os
from app import app

@pytest.fixture
def test_app():
    app.config.update({"TESTING": True})
    yield app

@pytest.fixture
def client(test_app):
    return test_app.test_client()

def setup_module(module):
    """
    Runs once before all tests in this file.
    Create or reset 'water.json' and 'water123.json' with known data.
    """
    with open('water.json', 'w') as f:
        json.dump({"water": 70}, f)

    with open('water123.json', 'w') as f:
        json.dump({"water": 5}, f)

def teardown_module(module):
    """
    Runs once after all tests finish.
    We'll clean up only user-specific files, but keep water.json.
    """
    if os.path.exists('water123.json'):
        os.remove('water123.json')
    # Remove water999.json if it was created by auto-create tests.
    if os.path.exists('water999.json'):
        os.remove('water999.json')

def test_root_404(client):
    """
    The root '/' isn't defined, so we expect a 404.
    """
    response = client.get("/")
    assert response.status_code == 404

def test_water_route(client):
    """
    /water should return whatever is in water.json (initially {"water": 70}).
    """
    response = client.get("/water")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["water"] == 70

def test_add_water_route(client):
    """
    /add_water should add 10 to 'water'.
    """
    before_resp = client.get("/water")
    before_data = json.loads(before_resp.data)
    before_amount = before_data["water"]

    add_resp = client.get("/add_water")
    assert add_resp.status_code == 200
    after_data = json.loads(add_resp.data)

    # Check that water was incremented by 10
    assert after_data["water"] == before_amount + 10
    # Check that 'adding' list was appended
    assert "adding" in after_data
    assert after_data["adding"][-1]["quantity"] == 10

def test_add_water_user_route(client):
    """
    /add_water/<user_id> with user_id=123
    should add 10 to water in water123.json (initially 5 -> now 15).
    """
    resp = client.get("/add_water/123")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["water"] == 15

def test_check_alert_missing_water(client):
    """
    Reset water123.json to below 10 to test alert scenario.
    """
    with open('water123.json', 'w') as f:
        json.dump({"water": 5}, f)

    resp = client.get("/add_alert/123")
    assert resp.status_code == 200
    assert resp.data.decode() == "alert missing water"

def test_check_alert_ok(client):
    """
    Set water123.json to >= 10 to test 'everything is ok'.
    """
    with open('water123.json', 'w') as f:
        json.dump({"water": 12}, f)

    resp = client.get("/add_alert/123")
    assert resp.status_code == 200
    assert resp.data.decode() == "everything is ok"

def test_auto_create_water_json(client):
    """
    Remove water.json if it exists, then call /water 
    to ensure read_water() auto-creates the file.
    """
    if os.path.exists('water.json'):
        os.remove('water.json')

    resp = client.get("/water")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    # Because the file didn't exist, code auto-created it with {"water": 0}
    assert data["water"] == 0

def test_auto_create_user_file(client):
    """
    Remove water999.json if it exists, then call /add_alert/999
    to ensure read_water_by_user() auto-creates the file with {"water": 0}.
    Then because water < 10 => 'alert missing water'
    """
    user_file = 'water999.json'
    if os.path.exists(user_file):
        os.remove(user_file)

    resp = client.get("/add_alert/999")
    assert resp.status_code == 200
    assert resp.data.decode() == "alert missing water"

    # Verify the file was created
    assert os.path.exists(user_file), "water999.json should be auto-created"

    # Optionally check the contents
    with open(user_file, 'r') as f:
        content = json.load(f)
        assert content["water"] == 0
