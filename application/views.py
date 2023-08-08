from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Annotation, Recruitment
from . import db
import json
from werkzeug.security import generate_password_hash
from .utils import populate_data

views = Blueprint('views', __name__)


# Home
@views.route('/')
@views.route('/home/')
def home():
    return render_template("home.html", user=current_user)

# Admin
@views.route('/admin/', methods=['GET', 'POST'])
@login_required
def admin():
    # Check if the user is admin or not
    if not current_user.is_admin:
        return "Không có quyền truy cập vào trang quản trị admin.", 403

    import os
    all_users = User.query.all()
    current_files = os.listdir('data/')

    return render_template(
        "admin.html",
        user=current_user,
        users=all_users,
        files=current_files
    )

# Admin: Add user
@views.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        return "Không có quyền truy cập vào trang quản trị admin.", 403

    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        is_admin = bool(request.form.get('is_admin'))

        new_user = User(
            email=email,
            username=username,
            password=generate_password_hash(password, method='sha256'),
            is_admin=is_admin
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Thêm user thành công.', 'success')
        return redirect(url_for('views.admin'))  # Redirect back to the user list page

    return render_template('views.admin')


# Admin: Remove user
@views.route('/admin/remove_user/<int:user_id>', methods=['POST', 'DELETE'])
@login_required
def remove_user(user_id):
    if not current_user.is_admin:
        return "Không có quyền truy cập vào trang quản trị admin.", 403

    if request.method in ['POST', 'DELETE']:
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            flash('Xóa user thành công.', 'success')
        else:
            flash('User không tồn tại.', 'danger')

        return redirect(url_for('views.admin'))


# Upload CSV data
@views.route('/admin/upload_csv', methods=['POST'])
@login_required
def upload_csv():
    if not current_user.is_admin:
        return "Không có quyền truy cập vào trang quản trị admin.", 403

    if request.method == 'POST':
        csv_file = request.files['csv_file']
        if csv_file and csv_file.filename.endswith('.csv'):
            # Remove all
            import os
            dir = 'data/'
            for f in os.listdir(dir):
                os.remove(os.path.join(dir, f))

            # Save
            filename = csv_file.filename
            csv_file.save('data/' + filename)
            flash('Upload thành công.', 'success')

            # Populate
            import pandas as pd
            populate_data(db, pd.read_csv('data/' + filename))
            flash('Populate thành công.', 'success')
            
        else:
            flash('File không hợp lệ.', 'danger')

    return redirect(url_for('views.admin'))


# View Data
@views.route('/view-data', methods=['GET', 'POST'])
@login_required
def view_data():
    if not current_user.is_admin:
        return "Không có quyền truy cập vào trang quản trị admin.", 403

    data = User.query.all()
    if request.method == 'POST':
        table_selected = request.form['table-select']
        if table_selected == 'recruitment':
            data = Recruitment.query.all()
        elif table_selected == 'annotation':
            data = Annotation.query.all()

    # Convert into list of dict
    data = [d.__dict__ for d in data]
    for d in data:
        d.pop('_sa_instance_state', None)

    return render_template(
        "view_data.html",
        user=current_user,
        data=data,
    )


# Annotate
@views.route('/annotate/', methods=['GET', 'POST'])
@login_required
def annotate():
    # Handle args
    rcmt_idx = request.args.get('index')
    count = Recruitment.query.count()
    n_completed = Annotation.query.filter_by(user_id=current_user.id).count()

    if rcmt_idx is None:
        return redirect(url_for('views.annotate', index=n_completed + 1))

    try:
        rcmt_idx = int(rcmt_idx)
        if rcmt_idx < 1:
            flash(f'Index cần phải lớn hơn hoặc bằng 1 ! redirect về index 1. Index bạn yêu cầu: {rcmt_idx}', category='error')
            return redirect(url_for('views.annotate', index=1))
        elif rcmt_idx > count:
            flash(f'Index lớn hơn phạm vi! redirect về index cuối cùng. Index bạn yêu cầu: {rcmt_idx}, tối đa: {count}', category='error')
            return redirect(url_for('views.annotate', index=count))
    except ValueError:
        flash(f'Index không hợp lệ! Index phải là số, redirect về index 1. Index bạn yêu cầu: {rcmt_idx}', category='error')
        return redirect(url_for('views.annotate', index=1))
    
    # Handle GET (to show recruitment data)
    recruitment_data = get_recruitment_data(rcmt_idx)
    rcmt_id = recruitment_data['other_aspect']['id']
    annotation_data = get_annotation_data(rcmt_id, current_user.id)

    # Handle POST (to label recruitment sample)
    if request.method == 'POST':
        aspects = recruitment_data.keys()
        aspect_level, label, explanation = get_form_data(aspects, request.form)
        insert_annotation(rcmt_id, current_user.id, aspect_level, label, explanation)
        flash(f'Gán / cập nhật nhãn mẫu dữ liệu số {rcmt_idx} thành công, chuyển tiếp đến mẫu kế tiếp!', category='success')
        return redirect(url_for('views.annotate', index=int(rcmt_idx) + 1))
    
    return render_template(
        "annotate.html",
        current_idx=rcmt_idx,
        user=current_user,
        rcmt_idx=rcmt_idx,
        last=count,
        n_completed=n_completed,
        rcmt_data=recruitment_data,
        ann_data=annotation_data
    )


def get_recruitment_data(idx):
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


def insert_annotation(r_id, u_id, aspect_level, label, explanation):
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