import re
import time
from requests_futures.sessions import FuturesSession
from threading import Thread
from uritemplate import expand
from flask import Flask, session, redirect, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask.ext.micropub import MicropubClient

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'TESTTESTKEY'
db = SQLAlchemy(app)
micropub = MicropubClient(app, client_id='https://dc53dc54.ngrok.io')

re_name = re.compile(r'name=([^:]+)')
re_end  = re.compile(r'end=([^:]+)')
re_end_fix = re.compile(r'(\d{8})(\d{6}).*')


def num_or(n):
    if isinstance(n, str) and len(n) > 0:
        return int(n)
    return n


class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    log_uri_template = db.Column(db.Text)


class ServerLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.Text)
    position = db.Column(db.Integer)
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'))
    server = db.relationship('Server', backref=db.backref('logs', lazy='dynamic'))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.Text)
    micropub_uri = db.Column(db.Text)
    access_token = db.Column(db.Text)


class UserOnServer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    auto_pub_threshold = db.Column(db.Integer)
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'))
    server = db.relationship('Server', backref=db.backref('server_users', lazy='dynamic'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('user_servers', lazy='dynamic'))


@app.route('/')
def index():
    print(session)
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
    print('success!', resp.me, resp.access_token, resp.next_url, resp.error)
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


def process_log(text, user, respect_threshold=False):
    print(text)
    print(user)


def follow_logs():
    http = FuturesSession()
    while True:
        s = db.session()
        logs = s.query(ServerLog).all()
        head_reqs = [http.head(log.uri) for log in logs]
        logs_to_get = [(log, req.result().headers['Content-Length'])
                       for log, req in zip(logs, head_reqs)
                       if int(req.result().headers['Content-Length']) > log.position]
        for log, new_len in logs_to_get:
            print('%s now available bytes=%s-%s' % (log.uri, log.position, new_len))
        get_reqs = [http.get(log.uri, stream=True, headers={
                        'range': 'bytes=%s-%s' % (log.position, new_len)
                    }) for log, new_len in logs_to_get]
        for (log, _), req in zip(logs_to_get, get_reqs):
            resp = req.result()
            if resp.status_code != 206:
                print('%s status: %s' % (log.uri, resp.status_code))
                continue
            print('%s reading' % log.uri)
            log.position += int(resp.headers['Content-Length'])
            for line in resp.iter_lines():
                if not line:
                    continue
                line = line.decode('utf-8', errors='replace')
                name = next(iter(re_name.findall(line)), None)
                end = next(iter(re_end.findall(line)), None)
                if not (name and end):
                    print('could not parse log entry: %s' % line)
                    continue
                account = UserOnServer.query.filter_by(server=log.server, name=name).first()
                if not account:
                    print('no account found for %s on server %s' % (name, log.server.name))
                    continue
                end = re_end_fix.sub(r'\1-\2', end)
                end = end[:4] + str(int(end[4:6]) + 1).zfill(2) + end[6:] # WTF
                log_uri = expand(log.server.log_uri_template, {'name': name, 'end': end})
                text = http.get(log_uri).result().text
                process_log(text, account.user, respect_threshold=True)
            print('%s now at byte %s' % (log.uri, log.position))
            s.add(log)
        s.commit()
        time.sleep(60)


def setup_db():
    db.create_all()
    s = db.session()
    cao = Server(id=0, name='crawl.akrasiac.org', log_uri_template='http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt')
    cszo = Server(id=1, name='crawl.s-z.org', log_uri_template='http://dobrazupa.org/morgue/{name}/morgue-{name}-{end}.txt')
    [s.merge(server) for server in [cao, cszo]]
    [s.merge(log) for log in [
        ServerLog(id=0, uri='http://crawl.akrasiac.org/logfile-git', server=cao),
        ServerLog(id=1, uri='http://crawl.akrasiac.org/logfile10', server=cao),#, position=27951741),
        ServerLog(id=2, uri='http://crawl.akrasiac.org/logfile11', server=cao),#, position=13018117),
        ServerLog(id=3, uri='http://crawl.akrasiac.org/logfile12', server=cao),#, position=23945857),
        ServerLog(id=4, uri='http://crawl.akrasiac.org/logfile13', server=cao),#, position=26046722),
        ServerLog(id=5, uri='http://crawl.akrasiac.org/logfile14', server=cao),#, position=29912966),
        ServerLog(id=6, uri='http://crawl.akrasiac.org/logfile15', server=cao),#, position=62616756),
        ServerLog(id=7, uri='http://crawl.akrasiac.org/logfile16', server=cao),#, position=66421016),
        ServerLog(id=8, uri='http://crawl.akrasiac.org/logfile17', server=cao),#, position=50321159),
        ServerLog(id=9, uri='http://dobrazupa.org/meta/git/logfile', server=cszo),#, position=398588930),
        ServerLog(id=10, uri='http://dobrazupa.org/meta/0.10/logfile', server=cszo),#, position=1376098),
        ServerLog(id=11, uri='http://dobrazupa.org/meta/0.11/logfile', server=cszo),#, position=32006985),
        ServerLog(id=12, uri='http://dobrazupa.org/meta/0.12/logfile', server=cszo),#, position=26769971),
        ServerLog(id=13, uri='http://dobrazupa.org/meta/0.13/logfile', server=cszo),#, position=27188919),
        ServerLog(id=14, uri='http://dobrazupa.org/meta/0.14/logfile', server=cszo),#, position=20215651),
        ServerLog(id=15, uri='http://dobrazupa.org/meta/0.15/logfile', server=cszo),#, position=38427072),
        ServerLog(id=16, uri='http://dobrazupa.org/meta/0.16/logfile', server=cszo),#, position=29009664),
        ServerLog(id=17, uri='http://dobrazupa.org/meta/0.17/logfile', server=cszo),#, position=45598649),
    ]]
    s.commit()


if __name__ == "__main__":
    setup_db()
    Thread(target=follow_logs).start()
    from aiohttp_wsgi import serve
    app.debug = True
    serve(app)