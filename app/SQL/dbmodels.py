from sqlalchemy.testing import db


# Defining the database models. model represents a table in a database.
class CourseAccess():
    db.Model = current_app.db.Model
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    module_code = db.Column(db.String(50), nullable=False)
    presentation_code = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<CourseAccess {self.user_id} {self.module_code} {self.presentation_code}>'
