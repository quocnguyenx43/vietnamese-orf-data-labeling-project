

def create_admin(db):
    from .models import User
    from werkzeug.security import generate_password_hash

    if not User.query.filter_by(username='admin').first():
        admin = User(
            email="",
            username='admin',
            password=generate_password_hash('adminteamlabeling', method='sha256'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

def populate_data(db, df):
    from .models import Recruitment
    db.session.query(Recruitment).delete()
    db.session.commit()
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