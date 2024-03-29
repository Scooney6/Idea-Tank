from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField
from wtforms.validators import InputRequired, Length, ValidationError
import mysql.connector
from my_app import config


# MySQL Connection helper function
def connect():
    return mysql.connector.connect(user=config.user, password=config.password,
                                   host=config.host,
                                   database=config.database)


# makes the home join form with validators
class HomeJoinForm(FlaskForm):
    username = StringField('username_label', validators=[InputRequired(message="Username Required"),
                                                         Length(min=4,
                                                                max=16,
                                                                message="Username must be between 4 and 16 characters")])
    join_code = IntegerField('join_code_label', validators=[InputRequired(message="Session Code Required")])
    join_button = SubmitField('Join')

    # custom validator for join_code
    def validate_join_code(self, join_code):
        with connect() as con:
            cur = con.cursor()
            cur.execute("SELECT RoomID FROM Rooms WHERE RoomID = %s", (join_code.data,))
            roomobj = cur.fetchone()
            if not roomobj:
                raise ValidationError("Incorrect room ID")

    # custom validator to prevent duplicate usernames
    def validate_username(self, field):
        with connect() as con:
            cur = con.cursor()
            cur.execute("SELECT Username FROM Users WHERE Username = %s AND RoomID = %s",
                        (field.data, self.join_code.data))
            roomobj = cur.fetchone()
            if roomobj:
                raise ValidationError("Name already exists!")


# makes the create session form
class CreateForm(FlaskForm):
    topic = StringField('topic_label', validators=[InputRequired()])
    time_limit = SelectField('Time Limit', choices=[('30', '30 Seconds'),
                                                    ('60', '1 Minute'),
                                                    ('120', '2 Minutes'),
                                                    ('600', '5 Minutes')])
    create_button = SubmitField('Create')
    username = StringField('username_label', validators=[InputRequired(message="Username Required"),
                                                         Length(min=4,
                                                                max=16,
                                                                message="Username must be between 4 and 16 characters")])
