from flask_sqlalchemy import SQLAlchemy
from flask import Flask, redirect, render_template, request
import agent
from dotenv import load_dotenv
import os
load_dotenv()



app = Flask(__name__)

# Prefer full URI if provided; otherwise compose it from Postgres env vars.

db_user = os.getenv("POSTGRES_USER", "postgres")
db_password = os.getenv("POSTGRES_PASSWORD", "postgres")
db_host = os.getenv("POSTGRES_HOST", "localhost")
db_port = os.getenv("POSTGRES_PORT", "5432")
db_name = os.getenv("POSTGRES_DB", "taskdb")
db_uri = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable = False)


@app.route("/", methods=['GET'])
def index():
    tasks = Task.query.order_by(Task.id).all()
    return render_template("index.html", tasks=tasks, ai_insight=None)

@app.route("/add", methods=['POST'])
def add():
    task_name = request.form.get("task")
    if task_name:
        new_task = Task(name = task_name)
        db.session.add(new_task)
        db.session.commit()
    return redirect("/")

@app.route("/tasks/<int:task_id>", methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        return {"error": "Task not found"}, 404
    
    db.session.delete(task)
    db.session.commit()
    return {"message": "Deleted"}

@app.route("/tasks/<int:task_id>/edit", methods=['GET'])
def edit_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        return "Task not found", 404
    
    return render_template("edit.html", task=task)

@app.route("/tasks/<int:task_id>", methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    task = Task.query.get(task_id)

    if not task:
        return {"error": "Task not found"}, 404
    
    task.name = data["name"]
    db.session.commit()

    
    return {"message": "Updated", "task": task}


@app.route("/tasks/AI", methods=['GET'])
def AI_insights():
    tasks = Task.query.order_by(Task.id).all()
    if not tasks:
        return "Tasks not found", 404
    
    
    
    task_names = [task.name for task in tasks]
    insights_from_ai = agent.insight_task(task_names)

    
    
    return render_template("index.html", tasks=tasks, ai_insight=insights_from_ai)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)