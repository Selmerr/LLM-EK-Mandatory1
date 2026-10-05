import pytest
from flask import json

@pytest.fixture(scope="module")
def client():
    app = Flask(__name__)
    app.config['TESTING'] = True
    from mikkel_workflow.src.llm_man_1.api import create_app
    app = create_app()
    with app.test_client() as client:
        yield client

def test_get_notes(client):
    response = client.get('/notes')
    assert response.status_code == 200
    notes = json.loads(response.data)
    # Empty list is valid, so just ensure JSON is returned
    assert isinstance(notes, list)

def test_create_note_valid(client):
    payload = {
        "title": "Test Note",
        "content": "This is a test note."
    }
    response = client.post('/notes', json=payload)
    assert response.status_code == 201
    created_note = json.loads(response.data)
    # Ensure ID was captured correctly
    assert 'id' in created_note

def test_create_note_missing_fields(client):
    payload = {
        "content": "This is a test note."
    }
    response = client.post('/notes', json=payload)
    assert response.status_code == 400
    error_msg = json.loads(response.data).get('error')
    assert error_msg == 'Title and content are required'

def test_delete_note_existing(client):
    # Create a note first
    payload = {
        "title": "Delete Me",
        "content": "Content for deletion."
    }
    create_response = client.post('/notes', json=payload)
    created_id = json.loads(create_response.data).get('id')
    
    # Now delete it
    response = client.delete(f'/notes/{created_id}')
    assert response.status_code == 204

def test_delete_note_nonexistent(client):
    # Try deleting an ID that doesn't exist
    response = client.delete('/notes/999')
    assert response.status_code == 404
