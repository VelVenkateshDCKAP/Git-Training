from flask_wtf import FlaskForm
from wtforms import StringField, validators,SelectMultipleField, PasswordField, TextAreaField, DateTimeField, FieldList

from task_tracker.mongo.collections import users


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', [validators.Length(min=2, max=50), validators.DataRequired()], render_kw={"placeholder": "John"})
    last_name = StringField('Last Name', [validators.Length(min=2, max=50), validators.DataRequired()], render_kw={"placeholder": "Doe"})
    email = StringField('Email Address', [validators.Email(), validators.DataRequired()], render_kw={"placeholder": "johndoe@example.com"})
    course = StringField('Course Name', [validators.Length(min=3, max=50), validators.DataRequired()])
    phone_number = StringField('Phone Number', [
        validators.Length(min=5, max=50),
        validators.DataRequired()
    ])


class ConfirmUserForm(FlaskForm):
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Repeat Password')

class TaskForm(FlaskForm):
    task_name = StringField('Task Name', [validators.Length(min=2, max=50)], render_kw={"placeholder": "Task Title"})
    problem_statement = TextAreaField('Problem Statement', [validators.Length(min=2, max=1000)], render_kw={"placeholder": "Task Description"})
    input = TextAreaField('Sample Input', [validators.Length(min=2, max=1000)], render_kw={"placeholder": "Input Data"})
    output = TextAreaField('Output Data', [validators.Length(min=2, max=1000)], render_kw={"placeholder": "Expected Output"})
    hints = StringField('Hints', [validators.Length(min=0, max=1000)], render_kw={"placeholder": "Any Hints"})
    due_date = DateTimeField('Finish By', format='%Y-%m-%d', render_kw={"placeholder":"YYYY-MM-DD"})
    assignedTo = SelectMultipleField('Assign To', choices=[(data['email'], data['email'])for data in list(users.find({"role":"user"},{"email":1}))], coerce=str)
