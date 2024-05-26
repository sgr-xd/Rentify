from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        return f"User('{self.first_name}', '{self.last_name}', '{self.email}')"
    
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    place = db.Column(db.String(100), nullable=False)
    area = db.Column(db.String(100), nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    hospitals_nearby = db.Column(db.String(100), nullable=True)
    colleges_nearby = db.Column(db.String(100), nullable=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    liked_by = db.Column(db.ARRAY(db.Integer), nullable=False, default=[])
    likes = db.Column(db.Integer, nullable=False, default=0)

    seller = db.relationship('User', backref=db.backref('properties', lazy=True))

    def __repr__(self):
        return f"Property('{self.place}', '{self.area}', '{self.bedrooms}', '{self.bathrooms}')"
