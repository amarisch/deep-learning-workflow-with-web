from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, SelectField
from wtforms import Form, widgets, SelectMultipleField
from wtforms import widgets


class ReusableForm(Form):
    # username = TextField('Username:', validators=[validators.required()])
    # vmname = TextField('VM Name:', validators=[validators.required()])
    # password = TextField('Password:', validators=[validators.required(), validators.Length(min=3, max=35)])
    username = TextField('Username:')
    vmname = TextField('VM Name:')
    password = TextField('Password:')
    # vmoption = SelectField('VM Option:', \
    #         choices=[('cpu', 'CPU Only'), ('gpu', 'CPU + GPU')])
    # datadisk = SelectField('Data Disk Option:', \
    # 		choices=[('deeplearning', 'Deep Learning Datasets'), ('machinelearning', 'Machine Learning Datasets'),\
    # 		 			('all', 'Deep Learning & Machine Learning Datasets'), ('empty', 'No Dataset')])
 
    def reset(self):
        blankData = MultiDict([ ('csrf', self.reset_csrf() ) ])
        self.process(blankData)