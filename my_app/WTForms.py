from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField
from wtforms.validators import InputRequired, Length, ValidationError
import sqlite3 as sql


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
        with sql.connect("rooms.db") as con:
            cur = con.cursor()

            code = str(join_code)
            code = code[67:71]
            cur.execute("SELECT room FROM rooms WHERE room = (?)", (code,))
            roomobj = cur.fetchone()
            if not roomobj:
                raise ValidationError("Incorrect room ID")


# makes the create session form
class CreateForm(FlaskForm):
    topic = StringField('topic_label', validators=[InputRequired()])
    time_limit = SelectField('Time Limit', choices=[('30s', '30 Seconds'),
                                                    ('1m', '1 Minute'),
                                                    ('2m', '2 Minutes'),
                                                    ('5m', '5 Minutes')])
    create_button = SubmitField('Create')
    username = StringField('username_label', validators=[InputRequired(message="Username Required"),
                                                         Length(min=4,
                                                                max=16,
                                                                message="Username must be between 4 and 16 characters")])
