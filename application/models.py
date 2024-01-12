# Define all models
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


# User
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(150))
    is_admin = db.Column(db.Boolean, default=False)
    validated_user_id = db.Column(db.Integer)

    # Related to Annotation
    annotations = db.relationship('Annotation')


# Recruitment
class Recruitment(db.Model):
    index = db.Column(db.Integer, primary_key=True) # Index
    
    id = db.Column(db.Integer, unique=True) # Recruitment ID 
    index_for_annotator = db.Column(db.Integer)
    annotator_id = db.Column(db.Integer)

    url = db.Column(db.String(255))
    total_images = db.Column(db.Integer)
    title = db.Column(db.String(255))
    body = db.Column(db.String)
    job_type = db.Column(db.String(20))
    vacancy = db.Column(db.Integer)
    location = db.Column(db.String(200))
    company_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    contact_name = db.Column(db.String(50))
    uploaded_date = db.Column(db.String(50))
    submission_expired = db.Column(db.String(50))
    user_id = db.Column(db.Integer)
    is_anonymous = db.Column(db.Boolean)
    is_recruiters = db.Column(db.Boolean)
    contact_type = db.Column(db.String(50))
    salary_type = db.Column(db.String(50))
    min_salary = db.Column(db.String(20))
    max_salary = db.Column(db.String(20))
    experience = db.Column(db.String(400))
    education = db.Column(db.String(400))
    certification = db.Column(db.String(400))
    benefit = db.Column(db.String(400))
    gender = db.Column(db.String(10))
    year_of_birth = db.Column(db.Integer)
    age = db.Column(db.String(20))
    min_age = db.Column(db.Integer)
    max_age = db.Column(db.Integer)
    u_user_id = db.Column(db.Integer)
    u_full_name = db.Column(db.String(100))
    u_phone = db.Column(db.String(20))
    u_url = db.Column(db.String(100))
    u_ad_id = db.Column(db.Integer)
    u_created_date = db.Column(db.String(100))

    # Related to Annotation
    annotations = db.relationship('Annotation')


# Annotation
class Annotation(db.Model):
    recruitment_id = db.Column(db.Integer, db.ForeignKey('recruitment.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    # Aspects
    title_aspect = db.Column(db.Integer)
    desc_aspect = db.Column(db.Integer)
    company_aspect = db.Column(db.Integer)
    poster_aspect = db.Column(db.Integer)
    other_aspect = db.Column(db.Integer)

    # Label
    label = db.Column(db.String(10)) # clean, seeding, warning

    # Explanation
    explanation = db.Column(db.String(200))


class CrossCheckReviews(db.Model):
    recruitment_id = db.Column(db.Integer, db.ForeignKey('recruitment.id'), primary_key=True)
    validator_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    validated_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    # Cross check reviews
    cross_check_review = db.Column(db.String(200))