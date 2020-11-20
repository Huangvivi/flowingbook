from flask_login import login_required

from flowingbook.views.blueprint import views


@views.route('/drift/<int:gid>', methods=['GET', 'POST'])
@login_required
def send_drift(gid):
    pass




@views.route('/drift/<int:gid>', methods=['GET', 'POST'])
@login_required
def satisfy_wish(gid):
    pass

