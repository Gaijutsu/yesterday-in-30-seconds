from flask import Flask, jsonify, send_from_directory
from moviepy.editor import VideoFileClip
from _types.feed_types import Entry

app = Flask(__name__)

# Example entries
entries = [
    Entry("Title 1", "Text 1", "image1.jpg", "http://example.com/1"),
    Entry("Title 2", "Text 2", "image2.jpg", "http://example.com/2"),
]

# Serve the entries as JSON
@app.route('/api/entries')
def get_entries():
    return jsonify([entry.__dict__ for entry in entries])

# Serve static files (videos, images)
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)
