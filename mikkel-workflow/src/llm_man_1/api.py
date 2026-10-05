from flask import Flask, jsonify, request, abort
from llm_man_1.storage import list_notes, create_note, delete_note

app = Flask(__name__)

@app.route('/notes', methods=['GET'])
def get_notes():
    notes = list_notes()
    return jsonify(notes)

@app.route('/notes', methods=['POST'])
def add_note():
    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data:
        abort(400, "Missing title or content")
    
    result = create_note(data['title'], data['content'])
    return jsonify(result), 201

@app.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note_endpoint(note_id):
    try:
        delete_note(note_id)
        return '', 204
    except ValueError as e:
        abort(404, str(e))
