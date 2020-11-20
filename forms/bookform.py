from wtforms import Form, StringField, validators, IntegerField
from wtforms.fields import simple
from wtforms.validators import Length, NumberRange, DataRequired, Regexp


class SearchForm(Form):
    q = simple.StringField(
        validators=[
            validators.DataRequired(message='请输入需要查询的关键字'),
            validators.length(min=1, max=80, message='关键字长度必须大于%(min)d且小于%(max)d')
        ]
    )
    page = IntegerField(validators=[NumberRange(min=1, max=30)], default=1)


class TradeForm(Form):
    recipient_name = StringField(validators=[DataRequired(), Length(min=2, max=20, message='收件人姓名长度必须在2到20个字符之间')])
    mobile = StringField(validators=[DataRequired(), Regexp('^1[0-9]{10}$', 0, '请输入正确的手机号')])
    message = StringField()
    address = StringField(validators=[DataRequired(), Length(min=10, max=70, message='地址还不到10个字吗？尽量写详细一些吧')])
