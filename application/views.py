from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_file
from flask_login import login_required, current_user
from .models import User, Annotation, Recruitment
from . import db
import json
from werkzeug.security import generate_password_hash
from .utils import (
    populate_data, convert_to_csv, send_csv_as_download,
    get_recruitment_data, get_annotation_data, get_form_data, insert_annotation,
    generate_monitor
)
from .backup_to_drive import (
    authenticate, get_file_id_by_name, upload_file, download_file
)
from sqlalchemy import func


views = Blueprint('views', __name__)


# Home handle
@views.route('/')
@views.route('/home/')
def home():
    return render_template("home.html", user=current_user)


# Admin page handle
@views.route('/admin/', methods=['GET', 'POST'])
@login_required
def admin():
    # Check if the user is admin or not
    if not current_user.is_admin:
        return "Không có quyền truy cập vào trang quản trị admin.", 403

    import os
    all_users = User.query.all()
    current_files = os.listdir('data/')

    index_to_name = {
        1: "admin",
        2: "VQuoc",
        3: "TDuong",
        4: "BKhanh",
        5: "HTruong",
        6: "QNhu",
        7: "TDinh",
        8: "HGiang",
        9: "BHan",
        10: "Kiet",
        11: "HAnh"
    }
    monitors_query = db.session.query(Annotation.user_id, func.count().label('record_count')).group_by(Annotation.user_id).all()
    monitors_results = {}
    for each in monitors_query:
        monitors_results[index_to_name[each[0]]] = each[1]

    for each in monitors_results:
        print(each)

    return render_template(
        "admin.html",
        user=current_user,
        users=all_users,
        monitors=monitors_results,
        files=current_files
    )

# Admin: Add user handle
@views.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    # Check if the user is admin or not
    if not current_user.is_admin:
        return "Không có quyền truy cập vào trang quản trị admin.", 403

    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        is_admin = bool(request.form.get('is_admin'))

        # Add new user to db
        new_user = User(
            email=email,
            username=username,
            password=generate_password_hash(password, method='sha256'),
            is_admin=is_admin
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Thêm user thành công.', 'success')
        return redirect(url_for('views.admin'))

    return render_template('views.admin')


# Admin: Remove user handle
@views.route('/admin/remove_user/<int:user_id>', methods=['POST', 'DELETE'])
@login_required
def remove_user(user_id):
    # Check if the user is admin or not
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


# Admin: Upload CSV data handle
@views.route('/admin/upload_csv', methods=['POST'])
@login_required
def upload_csv():
    # Check if the user is admin or not
    if not current_user.is_admin:
        return "Không có quyền truy cập vào trang quản trị admin.", 403

    if request.method == 'POST':
        csv_file = request.files['csv_file']
        if csv_file and csv_file.filename.endswith('.csv'):
            # Remove all file in the current dir
            import os
            dir = 'data/'
            for f in os.listdir(dir):
                os.remove(os.path.join(dir, f))

            # Save file as current csv_file
            filename = csv_file.filename
            csv_file.save('data/' + filename)
            flash('Upload thành công.', 'success')

            # Populate data into db
            import pandas as pd
            populate_data(db, pd.read_csv('data/' + filename))
            flash('Populate thành công.', 'success')
            
        else:
            flash('File không hợp lệ.', 'danger')

    return redirect(url_for('views.admin'))


# Admin: View Data handle
@views.route('/view-data', methods=['GET', 'POST'])
@login_required
def view_data():
    # Check if the user is admin or not
    if not current_user.is_admin:
        return "Không có quyền truy cập vào trang quản trị admin.", 403

    data = User.query.all()
    if request.method == 'POST':
        table_selected = request.form['table-select']
        button_clicked = request.form.get('action')

        if table_selected == 'recruitment':
            data = Recruitment.query.all()
        elif table_selected == 'annotation':
            data = Annotation.query.all()

        if button_clicked == 'download':
            csv_data = convert_to_csv(data)
            return send_csv_as_download(csv_data, f'{table_selected}_downloaded.csv')

    # Convert into list of dict
    data = [d.__dict__ for d in data]
    for d in data:
        d.pop('_sa_instance_state', None)

    return render_template(
        "view_data.html",
        user=current_user,
        data=data,
    )


# Download db
@views.route('/download_db')
@login_required
def download_db():
    # Check if the user is admin or not
    if not current_user.is_admin:
        return "Không có quyền truy cập vào trang quản trị admin.", 403
    
    db_file_path = '../instance/database.db'
    return send_file(db_file_path, as_attachment=True, download_name='your_database.db')


# Refresh db from Google Drive
@views.route('/refresh_from_drive')
@login_required
def refresh_from_drive():
    # Check if the user is admin or not
    if not current_user.is_admin:
        return "Không có quyền truy cập vào trang quản trị admin.", 403
    
    download_file(drive_file_name="backup_database.db", local_dest_path='./instance/database.db')
    flash('Tải dabase backup từ Google Drive về hệ thống thành công !!!')
    return redirect(url_for('views.admin'))


# Upload db to Google Drive
@views.route('/upload_to_drive')
@login_required
def upload_to_drive():
    # Check if the user is admin or not
    if not current_user.is_admin:
        return "Không có quyền truy cập vào trang quản trị admin.", 403
    
    upload_file(local_file_path="./instance/database.db", dest_file_name='backup_database.db')
    flash('Upload dabase backup từ hệ thống lên Google Drive thành công !!!')
    return redirect(url_for('views.admin'))


# Annotate handle
@views.route('/annotate/', methods=['GET', 'POST'])
@login_required
def annotate():
    # Handle args
    rcmt_idx = request.args.get('index')
    count = Recruitment.query.count()
    # n_completed = Annotation.query.filter_by(user_id=current_user.id).count()

    merged_data_count = db.session.query(func.count()).select_from(Recruitment).join(
        Annotation, Annotation.recruiment_id == Recruitment.id
    ).filter(
        Annotation.user_id == current_user.id
    ).scalar()

    n_completed = merged_data_count

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

        # Download backup
        download_file(drive_file_name="backup_database.db", local_dest_path='./instance/database.db')

        # Insert data thành công
        insert_annotation(rcmt_id, current_user.id, aspect_level, label, explanation, db)
        flash(f'Gán / cập nhật nhãn mẫu dữ liệu số {rcmt_idx} thành công, chuyển tiếp đến mẫu kế tiếp!', category='success')

        # Backup thành công
        upload_file(local_file_path="./instance/database.db", dest_file_name='backup_database.db')
        flash('Upload dabase backup từ hệ thống lên Google Drive thành công !!!')
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
