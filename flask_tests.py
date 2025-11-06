import pytest
import json
from flask_backend import app, db, Task, Comment

@pytest.fixture
def client():
    # setup test config
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        
    # cleanup after tests
    with app.app_context():
        db.drop_all()

@pytest.fixture
def sample_task(client):
    # create a sample task for testing
    response = client.post('/api/tasks', 
                          json={'title': 'Test Task', 'description': 'Test description'})
    data = json.loads(response.data)
    return data['id']

# Test creating a comment
def test_add_comment(client, sample_task):
    response = client.post(f'/api/tasks/{sample_task}/comments',
                          json={'content': 'This is a test comment'})
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['content'] == 'This is a test comment'
    assert data['task_id'] == sample_task
    assert 'id' in data
    assert 'created_at' in data

# Test adding comment with empty content
def test_add_comment_empty_content(client, sample_task):
    response = client.post(f'/api/tasks/{sample_task}/comments',
                          json={'content': '   '})
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

# Test adding comment without content field
def test_add_comment_no_content(client, sample_task):
    response = client.post(f'/api/tasks/{sample_task}/comments',
                          json={})
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

# Test adding comment to non-existent task
def test_add_comment_invalid_task(client):
    response = client.post('/api/tasks/9999/comments',
                          json={'content': 'Test comment'})
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data

# Test getting all comments for a task
def test_get_comments(client, sample_task):
    # add a few comments first
    client.post(f'/api/tasks/{sample_task}/comments',
               json={'content': 'First comment'})
    client.post(f'/api/tasks/{sample_task}/comments',
               json={'content': 'Second comment'})
    
    # now fetch them
    response = client.get(f'/api/tasks/{sample_task}/comments')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    # should be ordered by newest first
    assert data[0]['content'] == 'Second comment'
    assert data[1]['content'] == 'First comment'

# Test getting comments for non-existent task
def test_get_comments_invalid_task(client):
    response = client.get('/api/tasks/9999/comments')
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data

# Test getting comments when there are none
def test_get_comments_empty(client, sample_task):
    response = client.get(f'/api/tasks/{sample_task}/comments')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 0

# Test updating a comment
def test_update_comment(client, sample_task):
    # create a comment first
    create_response = client.post(f'/api/tasks/{sample_task}/comments',
                                 json={'content': 'Original content'})
    comment_data = json.loads(create_response.data)
    comment_id = comment_data['id']
    
    # update it
    response = client.put(f'/api/comments/{comment_id}',
                         json={'content': 'Updated content'})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['content'] == 'Updated content'
    assert data['id'] == comment_id
    # updated_at should be different from created_at (though might be same in fast tests)

# Test updating non-existent comment
def test_update_comment_not_found(client):
    response = client.put('/api/comments/9999',
                         json={'content': 'Updated content'})
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data

# Test updating comment with empty content
def test_update_comment_empty_content(client, sample_task):
    # create a comment
    create_response = client.post(f'/api/tasks/{sample_task}/comments',
                                 json={'content': 'Original'})
    comment_id = json.loads(create_response.data)['id']
    
    # try updating with empty
    response = client.put(f'/api/comments/{comment_id}',
                         json={'content': ''})
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

# Test deleting a comment
def test_delete_comment(client, sample_task):
    # create a comment
    create_response = client.post(f'/api/tasks/{sample_task}/comments',
                                 json={'content': 'To be deleted'})
    comment_id = json.loads(create_response.data)['id']
    
    # delete it
    response = client.delete(f'/api/comments/{comment_id}')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data
    
    # verify it's actually gone
    get_response = client.get(f'/api/tasks/{sample_task}/comments')
    comments = json.loads(get_response.data)
    assert len(comments) == 0

# Test deleting non-existent comment
def test_delete_comment_not_found(client):
    response = client.delete('/api/comments/9999')
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
