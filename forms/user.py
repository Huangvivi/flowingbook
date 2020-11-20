from wtforms import Form, StringField, IntegerField, PasswordField
from wtforms.validators import Length, DataRequired, Email, ValidationError, EqualTo

from flowingbook.models.user import User


class LoginForm(Form):
    # nickname = StringField(validators=[DataRequired('昵称不能为空'), Length(2, 8, message='昵称需要2-8个字符')])
    password = PasswordField(validators=[DataRequired('密码不能为空'), Length(6, 32)])
    email = StringField(validators=[DataRequired(), Length(8, 64),
                                    Email(message='电子邮箱不符合规范')])


class RegisterForm(LoginForm):
    nickname = StringField(validators=[DataRequired('昵称不能为空'), Length(2, 8, message='昵称需要2-8个字符')])
    password = PasswordField(validators=[DataRequired('密码不能为空'), Length(6, 32)])
    email = StringField(validators=[DataRequired(), Length(8, 64),
                                    Email(message='电子邮箱不符合规范')])

    def validate_email(self, field):
        data = User.query.filter_by(email=field.data).first()
        if data:
            raise ValidationError('电子邮件已被注册')

    def validate_nickname(self, field):
        data = User.query.filter_by(nickname=field.data).first()
        if data:
            raise ValidationError('昵称已被注册')


class EmailForm(Form):
    email = StringField(validators=[DataRequired("请输入你的邮箱号码"), Email(message='电子邮箱不符合规范')])


class ResetPasswordForm(Form):
    password = PasswordField(validators=[
        DataRequired(), Length(6, 32, message="密码长度需要6到32个字符"),])
    confirm_password = PasswordField(validators=[
        DataRequired(), Length(6, 32),
        EqualTo('password', message="两次输入密码不相同")])