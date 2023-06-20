from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    # Add relationship
    signups = db.relationship('Signup', back_populates='activity', lazy=True)
    campers = association_proxy(
        "signups", "camper", creator=lambda camper: Signup(camper=camper)
    )
    # Add serialization rules
    serialize_only = ("id", "name", "difficulty")
    serialize_rules = ("-signups.activity", "-signups.camper")
    
    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    # Add relationship
    signups = db.relationship('Signup', back_populates='camper', lazy=True)
    # activities = association_proxy("signups", "activity")
    activities = association_proxy(
        "signups", "activity", creator=lambda activity: Signup(activity=activity)
    )
    
    # Add serialization rules
    serialize_only = ("id", "name", "age", "signups")
    serialize_rules = ("-signups.camper", "signups.activity.id", "signups.activity.name", "signups.activity.difficulty")
    # def to_dict(self, *args, **kwargs):
    #     # Check if the "nested" keyword argument is provided and if it equals "show"
    #     if kwargs.get('nested') == 'show':
    #         # Include nested relationships for the show route
    #         kwargs['nested'] = {'signups': {'exclude': ['camper']}}
    #     else:
    #         # Exclude nested relationships for other routes
    #         kwargs['nested'] = {'signups': {'exclude': ['activity', 'camper']}}
        
    #     return super().to_dict(*args, **kwargs)


    # Add validation
    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise AssertionError('Name is required')
        return name
    
    @validates('age')
    def validate_age(self, key, age):
        if not age or age < 8 or age > 18:
            raise AssertionError('age is required and must be between 8 and 18')
        return age
    
    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'), nullable=False)
    
    # Add relationships
    activity = db.relationship('Activity', back_populates='signups', lazy=True)
    camper = db.relationship('Camper', back_populates='signups', lazy=True)
    # Add serialization rules
    serialize_only = ("id", "time", "activity_id", "camper_id")
    serialize_rules = ("-activity.signups", "-camper.signups")
    # Add validation
    @validates('time')
    def validate_time(self, key, time):
        if type(time) is not int or time < 0 or time > 24:
            raise AssertionError('time is required and must be between 0 and 23')
        return time
    
    
    def __repr__(self):
        return f'<Signup {self.id}>'


# add any models you may need.
