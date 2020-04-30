from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

import os

app = Flask(__name__)
DB_CONNECTION_STRING = os.environ.get("DB_URI", "postgresql://postgres:mysecretpassword@localhost:5432/postgres")
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONNECTION_STRING
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    assigne = db.Column(db.String(255))
    
    def __init__(self, title, assigne, _id=None):
        self.title = title
        self.assigne = assigne
        if _id:
            self.id = _id

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "assigne": self.assigne
        }
    

@app.route('/')
def hello_world():
    return {"message": "Hello, World!"}

# Read operations
@app.route('/tasks', methods=["GET"])
def get_tasks():
    task_title = request.args.get("title", "")
    task_assigne = request.args.get("assigne", "")
    tasks = Task.query.filter(Task.title.contains(task_title)).filter(Task.assigne.contains(task_assigne)).order_by(Task.id).all()
    tasks = [task.to_dict() for task in tasks]

    return {"tasks": tasks}

@app.route('/tasks/<int:task_id>', methods=["GET"])
def get_task(task_id):
    task = Task.query.get(task_id)
    if task:
        return task.to_dict()
    return {}, 404

# Create operations
@app.route('/tasks/<int:task_id>', methods=["POST"])
def post_task(task_id):
    task_json = request.json
    new_task = Task(task_json["title"], task_json["assigne"], _id=task_id)

    db.session.add(new_task)
    db.session.commit()

    return {"message": "Task was successfully added."}, 200

# Update operations
@app.route('/tasks/<int:task_id>', methods=["PUT"])
def put_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return {}, 404
    task_json = request.json
    task.title = task_json["title"]
    task.assigne = task_json["assigne"]

    db.session.add(task)
    db.session.commit()

    return {"message": "Task was successfully deleted."}, 200

# Delete operations
@app.route('/tasks/<int:task_id>', methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return {}, 404
    
    db.session.delete(task)
    db.session.commit()

    return {"message": "Task was successfully deleted."}, 200


@app.route('/upload', methods=['POST'])
def upload_file():
    print(request.files)
    f = request.files['image']
    f.save('./uploads/images/' + secure_filename(f.filename))
    f = request.files['text_file']
    f.save('./uploads/texts/' + secure_filename(f.filename))

    return {"message": "Files saved"}



if __name__ == "__main__":
    app.run("0.0.0.0", port="5000", debug=True)
