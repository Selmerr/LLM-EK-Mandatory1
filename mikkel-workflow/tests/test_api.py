import pytest
from flask import json

# Mock the Flask test client for testing purposes
@pytest.fixture(scope="function")
def client():
    from llm_man_1.api import app
    with app.test_client() as client:
        yield client

def test_get_notes(client):
    # Test GET /notes returns a list of notes (empty list is valid)
    response = client.get('/notes')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)  # Ensure it's a JSON array

def test_post_note(client):
    payload = {
        "title": "Test Note",
        "content": "This is a test note."
    }
    response = client.post('/notes', json=payload)
    assert response.status_code == 201
    data = json.loads(response.data)
    # Ensure the response contains an id field for the created note
    assert 'id' in data

def test_delete_note(client):
    # Create a note first
    payload = {
        "title": "Delete Me",
        "content": "A note to be deleted."
    }
    create_response = client.post('/notes', json=payload)
    assert create_response.status_code == 201
    created_data = json.loads(create_response.data)
    note_id = created_data['id']

    # Now delete the note by ID
    response = client.delete(f'/notes/{note_id}')
    assert response.status_code == 204

def test_post_missing_fields(client):
    payload = {}  # Missing title and content fields
    response = client.post('/notes', json=payload)
    assert response.status_code in (400, 422)  # Expect a bad request or validation error

def test_delete_nonexistent_note(client):
    note_id = 999  # Arbitrary non-existent ID
    response = client.delete(f'/notes/{note_id}')
    assert response.status_code == 404  # Note not found
