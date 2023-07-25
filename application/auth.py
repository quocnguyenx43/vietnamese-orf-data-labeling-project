from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Đăng nhập thành công!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Mật khẩu không chính xác, vui lòng thử lại!', category='error')
        else:
            flash('Tên tài khoản không tồn tại!', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password')
        password2 = request.form.get('conf-password')

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
            new_user = User(
                email=email,
                username=username,
                password=generate_password_hash(password1, method='sha256')
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Thông tin tài khoản đã được gửi đến server, vui lòng chờ phản hồi từ admin!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)


def send_mail(email, username, password):
    pass

    # import smtplib
    # from email.mime.text import MIMEText
    # from email.mime.multipart import MIMEMultipart

    # # Your email credentials
    # sender_email = "your_email@gmail.com"  # Replace with your sender email address
    # sender_password = "your_password"  # Replace with your sender email password

    # # Recipient email address
    # recipient_email = "20521813@gm.uit.edu.vn"  # Replace with the recipient's email address

    # # Email subject and body
    # subject = "ĐĂNG KÝ TÀI KHOẢN LABELING"
    # body = f"""
    #     Yêu cầu đăng ký tài khoản
    #     Email: {email},
    #     Useranme: {username},
    #     Password: {password},
    # """