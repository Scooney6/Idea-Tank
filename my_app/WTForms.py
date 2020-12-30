from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import InputRequired, Length


# makes the home join form with validators
class HomeJoinForm(FlaskForm):
    username = StringField('username_label', validators=[InputRequired(message="Username Required"),
                                                         Length(min=4, max=16,
                                                                message="Username must be between 4 and 16 characters")])
    join_code = IntegerField('join_code_label', validators=[InputRequired(message="Session Code Required")])
    join_button = SubmitField('Join')

    # custom validator for join_code
    def validate_join_code(form, field):
        # TODO: implement join_code validation for length and available codes
        pass
