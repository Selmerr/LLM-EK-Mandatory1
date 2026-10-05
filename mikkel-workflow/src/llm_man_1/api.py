from flask import Flask, request, jsonify
from llm_man_1.storage import list_notes, create_note, delete_note

app = Flask(__name__)

@app.route('/notes', methods=['GET'])
def get_notes():
    notes = list_notes()
    return jsonify(notes), 200

@app.route('/notes', methods=['POST'])
def create_note():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    
    if not title or not content:
        return jsonify({'error': 'Title and content are required'}), 400
    
    note_id = create_note(title, content)
    new_note = {'id': note_id}
    return jsonify(new_note), 201

@app.route('/notes/<string:id>', methods=['DELETE'])
def delete_note_by_id(id):
    success = delete_note(id)
    if not success:
        return jsonify({'error': 'Note with given ID does not exist'}), 404
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
