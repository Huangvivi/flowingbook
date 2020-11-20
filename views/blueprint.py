from flask import Blueprint, render_template

views = Blueprint("views", __name__)


# @views.app_errorhandler(404)
# def error_404(e):
#     return render_template('404.html')
#
# @views.app_errorhandler(500)
# def error_500(e):
#     return "<h1>500了兄弟，等我修好</h1>"
