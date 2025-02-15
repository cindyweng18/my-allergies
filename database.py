from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import validates
import inflect

db = SQLAlchemy()
p = inflect.engine()

class Allergy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    @validates("name")
    def convert_to_singular(self, key, value):
        singular_name = p.singular_noun(value.strip().lower()) or value.strip().lower()
        return singular_name

    def __repr__(self):
        return f"<Allergy {self.name}>"