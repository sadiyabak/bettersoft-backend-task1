from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # relationship to comments
    comments = db.relationship('Comment', backref='task', lazy=True, cascade='all, delete-orphan')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()

# Routes

# Add a new comment to a task
@app.route('/api/tasks/<int:task_id>/comments', methods=['POST'])
def add_comment(task_id):
    # check if task exists
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    data = request.get_json()
    
    # validate input
    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400
    
    content = data['content'].strip()
    if len(content) == 0:
        return jsonify({'error': 'Content cannot be empty'}), 400
    
    # create new comment
    new_comment = Comment(content=content, task_id=task_id)
    
    try:
        db.session.add(new_comment)
        db.session.commit()
        
        return jsonify({
            'id': new_comment.id,
            'content': new_comment.content,
            'task_id': new_comment.task_id,
            'created_at': new_comment.created_at.isoformat(),
            'updated_at': new_comment.updated_at.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create comment'}), 500

# Get all comments for a task
@app.route('/api/tasks/<int:task_id>/comments', methods=['GET'])
def get_comments(task_id):
    # verify task exists
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # fetch all comments for this task
    comments = Comment.query.filter_by(task_id=task_id).order_by(Comment.created_at.desc()).all()
    
    # build response
    comments_list = []
    for comment in comments:
        comments_list.append({
            'id': comment.id,
            'content': comment.content,
            'task_id': comment.task_id,
            'created_at': comment.created_at.isoformat(),
            'updated_at': comment.updated_at.isoformat()
        })
    
    return jsonify(comments_list), 200

# Update a comment
@app.route('/api/comments/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    # find the comment
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404
    
    data = request.get_json()
    
    # validate
    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required'}), 400
    
    new_content = data['content'].strip()
    if len(new_content) == 0:
        return jsonify({'error': 'Content cannot be empty'}), 400
    
    # update the comment
    comment.content = new_content
    comment.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        return jsonify({
            'id': comment.id,
            'content': comment.content,
            'task_id': comment.task_id,
            'created_at': comment.created_at.isoformat(),
            'updated_at': comment.updated_at.isoformat()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update comment'}), 500

# Delete a comment
@app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    # find the comment
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404
    
    try:
        db.session.delete(comment)
        db.session.commit()
        
        return jsonify({'message': 'Comment deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete comment'}), 500

# Helper route to create a task (for testing purposes)
@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    new_task = Task(
        title=data['title'],
        description=data.get('description', '')
    )
    
    try:
        db.session.add(new_task)
        db.session.commit()
        
        return jsonify({
            'id': new_task.id,
            'title': new_task.title,
            'description': new_task.description,
            'created_at': new_task.created_at.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create task'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
