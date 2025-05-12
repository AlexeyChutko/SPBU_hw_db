from flask_wtf import FlaskForm
import datetime
from datetime import datetime
from wtforms import StringField, FloatField, SubmitField, DateTimeField
from wtforms.validators import DataRequired

# Form for entering basic connection information
class CompoundForm(FlaskForm):
    name = StringField('Compound Name', validators=[DataRequired()])
    smiles = StringField('SMILES', validators=[DataRequired()])
    added_on = DateTimeField('Added On', default=datetime.utcnow)
    submit = SubmitField('Save Compound')

# Form for adding data on docking
class DockingForm(FlaskForm):
    score = FloatField('Docking Score')
    target = StringField('Target')
    method = StringField('Method')
    submit = SubmitField('Save Docking')

# Form for entering the ADMET profile
class ADMETForm(FlaskForm):
    solubility = StringField('Solubility')
    hepatotoxicity = StringField('Hepatotoxicity')
    bioavailability = StringField('Pgp substrate')
    submit = SubmitField('Save ADMET')

# A form for entering the results of molecular dynamics
class MDSimulationForm(FlaskForm):
    avg_rmsd = FloatField('Average RMSD')
    avg_rmsf = FloatField('Average RMSF')
    interactions = FloatField('ΔG')

    submit = SubmitField('Save MD')
