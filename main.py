from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from datetime import date


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy()
db.init_app(app)


# CONFIGURE TABLES
class Tasks(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    completed = db.Column(db.Boolean, nullable=False)
    task = db.Column(db.String(100), unique=False)
    date = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        new_task = Tasks(
            task=request.form['task'],
            completed=False,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('index'))
    return redirect(url_for('index'))


@app.route("/check/<int:task_id>")
def check(task_id):
    task_to_modify = db.get_or_404(Tasks, task_id)
    task_to_modify.completed = True
    db.session.commit()
    return redirect(url_for('index'))


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    task_to_delete = db.get_or_404(Tasks, task_id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/process_selection', methods=['POST'])
def process_selection():
    selected_filter = request.form.get('filter')
    if selected_filter:
        if selected_filter == "done":
            tasks = Tasks.query.filter_by(completed=True).all()
        elif selected_filter == "pending":
            tasks = Tasks.query.filter_by(completed=False).all()
        else:
            result = db.session.execute(db.select(Tasks))
            tasks = result.scalars().all()
        return render_template("index.html", tasks=tasks)
    else:
        return redirect(url_for('index'))


@app.route('/', methods=["GET", "POST"])
def index():
    result = db.session.execute(db.select(Tasks))
    tasks = result.scalars().all()
    return render_template("index.html", tasks=tasks)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
