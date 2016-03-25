from flask import session, redirect, url_for, request, render_template
from conf import *
from models import *
from util import *
from processing import process_log


@app.route('/')
def index():
    if 'me' in session:
        user = User.query.filter_by(uri=session['me']).first()
        servers = Server.query.all()
        return render_template('index.html', user=user, servers=servers)
    else:
        return render_template('index.html')


@app.route('/server-accounts', methods=['POST'])
def server_account_new():
    user = User.query.filter_by(uri=session['me']).first_or_404()
    server = Server.query.get(int(request.form['server_id']))
    account = UserOnServer(
        name=request.form['name'],
        auto_pub_threshold=num_or(request.form['auto_pub_threshold']),
        user=user,
        server=server
    )
    db.session.add(account)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/server-accounts/<int:account_id>', methods=['POST'])
def server_account_edit(account_id):
    account = UserOnServer.query.get_or_404(account_id)
    if 'delete' in request.args:
        db.session.delete(account)
    else:
        account.name = request.form['name']
        account.auto_pub_threshold = num_or(request.form['auto_pub_threshold'])
        account.server = Server.query.get_or_404(request.form['server_id'])
        db.session.add(account)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/upload-log', methods=['POST'])
def upload_log():
    user = User.query.filter_by(uri=session['me']).first_or_404()
    process_log(request.files['file'].read(), user)
    return redirect(url_for('index'))

@app.route('/login')
def login():
    return micropub.authorize(me=request.args.get('me'), scope='post')

@app.route('/logout')
def logout():
    session['me'] = None
    return redirect(url_for('index'))

@app.route('/micropub-callback')
@micropub.authorized_handler
def micropub_callback(resp):
    session['me'] = resp.me
    user = User.query.filter_by(uri=resp.me).first()
    if user:
        user.micropub_uri = resp.micropub_endpoint
        user.access_token = resp.access_token
        db.session.add(user)
    else:
        db.session.add(User(uri=resp.me, micropub_uri=resp.micropub_endpoint, access_token=resp.access_token))
    db.session.commit()
    return redirect(url_for('index'))
