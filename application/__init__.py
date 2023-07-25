from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs' # random key
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User
    
    with app.app_context():
        db.create_all()
        populate_recruitment_table(db)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app


def create_database(app):
    if not path.exists('instance/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')


def populate_recruitment_table(db):
    from .models import Recruitment
    import pandas as pd
    if Recruitment.query.count() == 0:
        df = pd.read_csv('data/sample_250_seed_100.csv') 
        for _, row in df.iterrows():
            recruitment = Recruitment(
                id=row['id'],
                url=row['url'],
                total_images=row['total_images'],
                title=row['title'],
                body=row['body'],
                job_type=row['job_type'],
                vacancy=row['vacancy'],
                location=row['location'],
                company_name=row['company_name'],
                phone=row['phone'],
                contact_name=row['contact_name'],
                uploaded_date=row['uploaded_date'],
                submission_expired=row['submission_expired'],
                user_id=row['user_id'],
                is_anonymous=row['is_anonymous'],
                is_recruiters=row['is_recruiters'],
                contact_type=row['contact_type'],
                salary_type=row['salary_type'],
                min_salary=row['min_salary'],
                max_salary=row['max_salary'],
                experience=row['experience'],
                education=row['education'],
                certification=row['certification'],
                benefit=row['benefit'],
                gender=row['gender'],
                year_of_birth=row['year_of_birth'],
                age=row['age'],
                min_age=row['min_age'],
                max_age=row['max_age'],
                u_user_id=row['u.user_id'],
                u_full_name=row['u.full_name'],
                u_phone=row['u.phone'],
                u_url=row['u.url'],
                u_ad_id=row['u.ad_id'],
                u_created_date=row['u.created_date']
            )
            db.session.add(recruitment)
        db.session.commit()