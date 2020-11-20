from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, login_required, logout_user
from flowingbook.forms.user import RegisterForm, LoginForm, EmailForm, ResetPasswordForm
# from itsdangerous import
from flowingbook.models.base import db
from flowingbook.models.user import User
from flowingbook.views.blueprint import views
from flowingbook.utils.email import send_mail


@views.route("/register", methods=['POST', 'GET'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        with db.auto_commit():
            user = User()
            user.set_attrs(form.data)
            db.session.add(user)
        return redirect(url_for('views.login'))
    return render_template("auth/register.html", form=form)


@views.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            next = request.args.get('next')
            # if not is_safe_url(next)
            #     return abort(400)
            # return redirect(next or url_for('views.index'))
            if not next:
                next = url_for('views.index')
            return redirect(next)
        else:
            flash('账号不存在或密码错误')
    return render_template('auth/login.html', form=form)


@views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.index'))


@views.route('/reset/password', methods=['GET', 'POST'])
def forget_password_request():
    form = EmailForm(request.form)
    if request.method == 'POST':
        if form.validate():
            account_email = form.email.data
            user = User.query.filter_by(email=account_email).first()
            if not user:
                flash("用户邮箱未注册")
                return render_template('auth/forget_password_request.html', form=form)
            token = user.generate_token()
            send_mail(form.email.data, '重置您的密码',
                      'email/reset_password.html', user=user, token=token)
            flash('一封邮件已发送到邮箱' + account_email + '，请及时查收')
            return redirect(url_for('views.login'))
    return render_template('auth/forget_password_request.html', form=form)
    pass


@views.route('/reset/password/<token>', methods=['GET', 'POST'])
def forget_password(token):
    form = ResetPasswordForm(request.form)
    print(form.password.data)
    print(form.confirm_password.data)
    if request.method == 'POST' and form.validate():
        success = User.reset_password(token, form.password.data)
        if success:
            flash('你的密码已更新,请使用新密码登录')
            return redirect(url_for('views.login'))
        else:
            flash('密码重置失败')
    #
    #   判断token是否被用过
    #   用过则跳转链接已失效
    return render_template('auth/forget_password.html', form=form)




@views.route("/personal_center")
def personal_center():
    pass
