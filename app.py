from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import or_
from models import db, Compound, Docking, ADMET, MDSimulation
from forms import CompoundForm, DockingForm, ADMETForm, MDSimulationForm
from rdkit import Chem
from rdkit.Chem import Draw
import io
import base64
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
db.init_app(app)

with app.app_context():
    db.create_all()

# The main page with a list of connections, the ability to sort and search
@app.route('/')
def index():
    sort = request.args.get('sort')
    search = request.args.get('search')

    # Initial query: connections + merging with MD simulation results
    query = Compound.query.outerjoin(MDSimulation)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Compound.name.ilike(search_filter),
                Compound.smiles.ilike(search_filter)
            )
        )

    if sort == 'interactions':
        query = query.order_by(MDSimulation.interactions.desc())
    else:
        query = query.order_by(Compound.id.asc())
        sort = None

    compounds = query.all()
    return render_template('index.html', compounds=compounds, current_sort=sort, search_query=search)


# The page for adding a new connection and related data (docking, ADMET, MD)
@app.route('/add', methods=['GET', 'POST'])
def add_compound():
    c_form = CompoundForm()
    d_form = DockingForm()
    a_form = ADMETForm()
    md_form = MDSimulationForm()

    if c_form.validate_on_submit():
        compound = Compound(name=c_form.name.data, smiles=c_form.smiles.data)
        db.session.add(compound)
        db.session.commit()

        # Adding related records: docking, ADMET, MD
        docking = Docking(
            compound_id=compound.id,
            score=d_form.score.data,
            target=d_form.target.data,
            method=d_form.method.data
        )
        admet = ADMET(
            compound_id=compound.id,
            solubility=a_form.solubility.data,
            hepatotoxicity=a_form.hepatotoxicity.data,
            bioavailability=a_form.bioavailability.data
        )
        md = MDSimulation(
            compound_id=compound.id,
            avg_rmsd=md_form.avg_rmsd.data,
            avg_rmsf=md_form.avg_rmsf.data,
            interactions=md_form.interactions.data
        )
        # Save all related records
        db.session.add_all([docking, admet, md])
        db.session.commit()

        return redirect(url_for('index'))
    compound = None
    return render_template('compound_form.html', c_form=c_form, d_form=d_form, a_form=a_form, md_form=md_form,compound=compound)

# Editing an existing connection
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_compound(id):
    # Getting a connection by ID or error
    compound = Compound.query.get_or_404(id)

    # Getting related data or creating new objects by default
    docking = compound.docking_scores[0] if compound.docking_scores else Docking(compound_id=id)
    admet = compound.admet_properties[0] if compound.admet_properties else ADMET(compound_id=id)
    md = compound.md_results[0] if compound.md_results else MDSimulation(compound_id=id)

    # Initializing forms with current data
    c_form = CompoundForm(obj=compound)
    d_form = DockingForm(obj=docking)
    a_form = ADMETForm(obj=admet)
    md_form = MDSimulationForm(obj=md)

    if c_form.validate_on_submit():
        c_form.populate_obj(compound)
        d_form.populate_obj(docking)
        a_form.populate_obj(admet)
        md_form.populate_obj(md)

        db.session.add_all([compound, docking, admet, md])
        db.session.commit()
        return redirect(url_for('index'))
    compound = None
    return render_template('compound_form.html', c_form=c_form, d_form=d_form, a_form=a_form, md_form=md_form, compound=compound)

# Deleting a connection by ID
@app.route('/delete/<int:id>', methods=['POST'])
def delete_compound(id):
    compound = Compound.query.get_or_404(id)
    db.session.delete(compound)
    db.session.commit()
    return redirect(url_for('index'))

# Viewing a single connection and generating a 2D image from SMILES
@app.route('/compound/<int:id>')
def view_compound(id):
    compound = Compound.query.get_or_404(id)

    # Generating an image of a molecule using Rdkit
    mol = Chem.MolFromSmiles(compound.smiles)
    if mol:
        img = Draw.MolToImage(mol, size=(300, 300))
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        smiles_img = f"data:image/png;base64,{img_str}"
    else:
        smiles_img = None

    return render_template("compound_detail.html", compound=compound, smiles_img=smiles_img)

# Launching the app
if __name__ == '__main__':
    app.run(debug=True)
