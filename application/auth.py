from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from .utils import send_mail
from .backup_to_drive import (
    authenticate, get_file_id_by_name, upload_file, download_file
)

auth = Blueprint('auth', __name__)


# Login handle
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if correct information
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                # Login successfully
                login_user(user, remember=True)
                flash('Đăng nhập thành công!', category='success')
                # Download backup data successfully
                download_file(drive_file_name="backup_database.db", local_dest_path='./instance/database.db')
                flash('Tải dabase backup từ Google Drive về hệ thống thành công !!!')
                return redirect(url_for('views.home'))
            else:
                flash('Mật khẩu không chính xác, vui lòng thử lại!', category='error')
        else:
            flash('Tên tài khoản không tồn tại!', category='error')

    return render_template("login.html", user=current_user)


# Logout handle
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# Sign up handle
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password')
        password2 = request.form.get('conf-password')

        # Check if the information is satified
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email đã tồn tại!', category='error')
        elif len(email) < 4:
            flash('Email tối thiểu 4 ký tự!', category='error')
        elif len(username) < 2:
            flash('Tên tài khoản tối thiếu 2 ký tự!.', category='error')
        elif password1 != password2:
            flash('Mật khẩu không khớp!', category='error')
        elif len(password1) < 7:
            flash('Mật khẩu tối thiểu 8 ký tự!.', category='error')
        else:
            # If everything is okay, send mail to admin
            send_mail(email=email, username=username, password=password1)
            flash('Thông tin tài khoản đã được gửi đến admin, xin chờ phản hồi.', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

