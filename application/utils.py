from flask import Flask, render_template, request, Response
import csv
import io


# Create admin account if admin account doesn't exists
def create_admin(db):
    from .models import User
    from werkzeug.security import generate_password_hash

    if not User.query.filter_by(username='admin').first():
        admin = User(
            email="",
            username='admin',
            password=generate_password_hash('adminadmin', method='sha256'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

# Populate data from `df`
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


# Convert `db Query` into csv file
def convert_to_csv(data):
    csv_data = []
    
    if data:
        # Get the fields from the first item in the list
        fields = list(data[0].__dict__.keys())
        
        # Exclude private and special attributes
        fields = [field for field in fields if not field.startswith('_') and field != 'metadata']
        
        # Append headers to the CSV data
        csv_data.append(fields)
        
        # Iterate through each item and extract field values
        for item in data:
            row = [getattr(item, field) for field in fields]
            csv_data.append(row)
        
    return csv_data


# Send csv as download file
def send_csv_as_download(data, filename):
    output = io.StringIO()  # Create a temporary file-like object
    
    csv_writer = csv.writer(output)
    csv_writer.writerows(data)  # Write the data to the file-like object
    
    # Create the Response object and set appropriate headers
    response = Response(output.getvalue(), content_type='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def send_mail(email, username, password):
    from email.message import EmailMessage
    import smtplib

    email_sender = 'hairapviet@gmail.com'
    email_password = 'yawxkeuwkcrcyahe'
    email_receiver = 'quocnguyenx43@gmail.com'

    subject = 'CREATING LABELING ACCOUNT REQUEST'

    body = "Request to create new account\n"
    body += "Email: " + email + "\n"
    body += "Username: " + username + "\n"
    body += "Password: " + password + "\n\n"

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_sender, email_password)
    server.sendmail(email_sender, email_receiver, em.as_string())


# Annotation handle
def get_recruitment_data(idx):
    from .models import Recruitment
    recruitment = Recruitment.query.filter_by(index=idx).first()
    aspects = {
        'title_aspect': ['title', 'job_type'],
        'desc_aspect': ['body', 'education', 'experience', 'benefit', 'certification'],
        'company_aspect': ['company_name', 'location', 'phone', 'contact_name'],
        'poster_aspect': ['u_user_id', 'u_full_name', 'u_phone', 'u_url', 'uploaded_date', 'submission_expired', 'u_created_date', 'is_anonymous', 'is_recruiters'],
        'other_aspect': ['id', 'url', 'vacancy', 'total_images', 'contact_type', 'salary_type', 'min_salary', 'max_salary', 'gender', 'year_of_birth', 'age', 'min_age', 'max_age']
    }
    recruitment = {col.name: getattr(recruitment, col.name) for col in recruitment.__table__.columns}
    data = {}
    for key, cols in aspects.items():
        data[key] = {}
        for col in cols:
            data[key][col] = recruitment[col]

    return data

def get_annotation_data(r_idx, u_idx):
    from .models import Annotation
    annotation = Annotation.query.filter_by(recruiment_id=r_idx, user_id=u_idx).first()
    try:
        data = {col.name: getattr(annotation, col.name) for col in annotation.__table__.columns}
    except:
        return None

    return data


def get_form_data(aspects, form):
    label = form.get('labeling_select')
    explanation = request.form.get('explanation')

    aspect_level = {}
    
    # Loop through each aspect in the form
    for aspect in aspects:
        aspect_value = request.form.get(aspect)
        aspect_level[aspect] = aspect_value
    

    return aspect_level, label, explanation


def insert_annotation(r_id, u_id, aspect_level, label, explanation, db):
    from .models import Annotation
    from flask import flash

    existing_annotation = Annotation.query.filter_by(recruiment_id=r_id, user_id=u_id).first()

    if existing_annotation:
        # If an annotation exists, update its fields
        existing_annotation.title_aspect = aspect_level['title_aspect']
        existing_annotation.desc_aspect = aspect_level['desc_aspect']
        existing_annotation.company_aspect = aspect_level['company_aspect']
        existing_annotation.poster_aspect = aspect_level['poster_aspect']
        existing_annotation.other_aspect = aspect_level['other_aspect']
        existing_annotation.label = label
        existing_annotation.explanation = explanation
        flash('Annotation updated!', category='success')
    else:
        new_annotation = Annotation(
            recruiment_id=r_id,
            user_id=u_id,
            title_aspect=aspect_level['title_aspect'],
            desc_aspect=aspect_level['desc_aspect'],
            company_aspect=aspect_level['company_aspect'],
            poster_aspect=aspect_level['poster_aspect'],
            other_aspect=aspect_level['other_aspect'],
            label=label,
            explanation=explanation
        )
        db.session.add(new_annotation)
        flash('Annotation added!', category='success')
    db.session.commit()