from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Compound model (main table)
class Compound(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    smiles = db.Column(db.String(255), nullable=False)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)

    # Compound to the Docking table — one compound can have multiple docking records
    docking_scores = db.relationship('Docking', backref='compound', cascade="all, delete-orphan")
    # Relationship to the ADMET table — one compound can have multiple ADMET profiles
    admet_properties = db.relationship('ADMET', backref='compound', cascade="all, delete-orphan")
    # Relation to the MDSimulation table — one compound can have multiple MDSimulation results
    md_results = db.relationship('MDSimulation', backref='compound', cascade="all, delete-orphan")

# A model for storing the results of molecular docking
class Docking(db.Model):
    id = db.Column(db.Integer, primary_key=True) # A foreign key for the connection, required
    compound_id = db.Column(db.Integer, db.ForeignKey('compound.id'), nullable=False)
    score = db.Column(db.Float)
    target = db.Column(db.String(100))
    method = db.Column(db.String(50))

# A model for storing the ADMET profile of a compound
class ADMET(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    compound_id = db.Column(db.Integer, db.ForeignKey('compound.id'), nullable=False)
    solubility = db.Column(db.String(50))
    hepatotoxicity = db.Column(db.String(50))
    bioavailability = db.Column(db.String(50))

# A model for storing the results of molecular dynamics
class MDSimulation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    compound_id = db.Column(db.Integer, db.ForeignKey('compound.id'), nullable=False)
    avg_rmsd = db.Column(db.Float)
    avg_rmsf = db.Column(db.Float)
    interactions = db.Column(db.Float)
