from conf import db


class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)


class ServerLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.Text)
    uri_template = db.Column(db.Text)
    crawl_month_fix = db.Column(db.Boolean)
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


def upsert_preserving_position(s, log):
    (id, server, uri, uri_template, crawl_month_fix, position) = log
    if s.query(ServerLog).get(id):
        s.merge(ServerLog(id=id, server=server, uri=uri, uri_template=uri_template, crawl_month_fix=crawl_month_fix))
    else:
        s.merge(ServerLog(id=id, server=server, uri=uri, uri_template=uri_template, crawl_month_fix=crawl_month_fix, position=position))


# check new data at: https://github.com/crawl/scoring/blob/master/sources.yml
def setup_db():
    db.create_all()
    s = db.session()
    cao    = Server(id=0, name='crawl.akrasiac.org')
    cszo   = Server(id=1, name='crawl.s-z.org')
    # cdo    = Server(id=2, name='crawl.develz.org') # Doesn't even return Content-Length
    clan   = Server(id=3, name='underhound.eu')
    cbro   = Server(id=4, name='crawl.berotato.org')
    cwz    = Server(id=5, name='webzook.net/soup')
    # lld    = Server(id=6, name='lazy-life.ddo.jp') # Doesn't support HEAD
    cxc    = Server(id=7, name='crawl.xtahua.com')
    # cpo    = Server(id=8, name='crawl.project357.org') # Content-Length
    cjr    = Server(id=9, name='crawl.jorgrun.rocks')
    [s.merge(server) for server in [cao, cszo]]
    [upsert_preserving_position(s, data) for data in [
         # DO NOT CHANGE ID!
        (0,       cao,     'http://crawl.akrasiac.org/logfile-git',               'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  301284125),
        (1,       cao,     'http://crawl.akrasiac.org/logfile10',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  27951741),
        (2,       cao,     'http://crawl.akrasiac.org/logfile11',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  13018117),
        (3,       cao,     'http://crawl.akrasiac.org/logfile12',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  23945857),
        (4,       cao,     'http://crawl.akrasiac.org/logfile13',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  26046722),
        (5,       cao,     'http://crawl.akrasiac.org/logfile14',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  29912966),
        (6,       cao,     'http://crawl.akrasiac.org/logfile15',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  62616756),
        (7,       cao,     'http://crawl.akrasiac.org/logfile16',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  66446547),
        (8,       cao,     'http://crawl.akrasiac.org/logfile17',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  52337094),
        (9,       cao,     'http://crawl.akrasiac.org/logfile18',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  0),
        (10,      cao,     'http://crawl.akrasiac.org/logfile19',                 'http://crawl.akrasiac.org/rawdata/{name}/morgue-{name}-{end}.txt',                True,  0),
        (1000,    cszo,    'http://dobrazupa.org/meta/git/logfile',               'http://dobrazupa.org/morgue/{name}/morgue-{name}-{end}.txt',                      True,  401360774),
        (1001,    cszo,    'http://dobrazupa.org/meta/0.10/logfile',              'http://dobrazupa.org/morgue/{name}/morgue-{name}-{end}.txt',                      True,  1376098),
        (1002,    cszo,    'http://dobrazupa.org/meta/0.11/logfile',              'http://dobrazupa.org/morgue/{name}/morgue-{name}-{end}.txt',                      True,  32006985),
        (1003,    cszo,    'http://dobrazupa.org/meta/0.12/logfile',              'http://dobrazupa.org/morgue/{name}/morgue-{name}-{end}.txt',                      True,  26769971),
        (1004,    cszo,    'http://dobrazupa.org/meta/0.13/logfile',              'http://dobrazupa.org/morgue/{name}/morgue-{name}-{end}.txt',                      True,  27188919),
        (1005,    cszo,    'http://dobrazupa.org/meta/0.14/logfile',              'http://dobrazupa.org/morgue/{name}/morgue-{name}-{end}.txt',                      True,  20215651),
        (1006,    cszo,    'http://dobrazupa.org/meta/0.15/logfile',              'http://dobrazupa.org/morgue/{name}/morgue-{name}-{end}.txt',                      True,  38427072),
        (1007,    cszo,    'http://dobrazupa.org/meta/0.16/logfile',              'http://dobrazupa.org/morgue/{name}/morgue-{name}-{end}.txt',                      True,  29014592),
        (1008,    cszo,    'http://dobrazupa.org/meta/0.17/logfile',              'http://dobrazupa.org/morgue/{name}/morgue-{name}-{end}.txt',                      True,  46370874),
        (1009,    cszo,    'http://dobrazupa.org/meta/0.18/logfile',              'http://dobrazupa.org/morgue/{name}/morgue-{name}-{end}.txt',                      True,  0),
        (3000,    clan,    'http://underhound.eu:81/crawl/meta/git/logfile',      'http://underhound.eu:81/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  89930316),
        (3001,    clan,    'http://underhound.eu:81/crawl/meta/0.10/logfile',     'http://underhound.eu:81/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  106071),
        (3002,    clan,    'http://underhound.eu:81/crawl/meta/0.11/logfile',     'http://underhound.eu:81/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  79132),
        (3003,    clan,    'http://underhound.eu:81/crawl/meta/0.12/logfile',     'http://underhound.eu:81/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  1632644),
        (3004,    clan,    'http://underhound.eu:81/crawl/meta/0.13/logfile',     'http://underhound.eu:81/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  8708102),
        (3005,    clan,    'http://underhound.eu:81/crawl/meta/0.14/logfile',     'http://underhound.eu:81/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  7359165),
        (3006,    clan,    'http://underhound.eu:81/crawl/meta/0.15/logfile',     'http://underhound.eu:81/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  7427725),
        (3007,    clan,    'http://underhound.eu:81/crawl/meta/0.16/logfile',     'http://underhound.eu:81/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  6529896),
        (3008,    clan,    'http://underhound.eu:81/crawl/meta/0.17/logfile',     'http://underhound.eu:81/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  20628703),
        (3009,    clan,    'http://underhound.eu:81/crawl/meta/0.18/logfile',     'http://underhound.eu:81/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  0),
        (3010,    clan,    'http://underhound.eu:81/crawl/meta/0.19/logfile',     'http://underhound.eu:81/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  0),
        (4000,    cbro,    'http://crawl.berotato.org/crawl/meta/git/logfile',    'http://crawl.berotato.org/crawl/morgue/{name}/morgue-{name}-{end}.txt',           True,  54048387),
        (4001,    cbro,    'http://crawl.berotato.org/crawl/meta/0.13/logfile',   'http://crawl.berotato.org/crawl/morgue/{name}/morgue-{name}-{end}.txt',           True,  424187),
        (4002,    cbro,    'http://crawl.berotato.org/crawl/meta/0.14/logfile',   'http://crawl.berotato.org/crawl/morgue/{name}/morgue-{name}-{end}.txt',           True,  3267516),
        (4003,    cbro,    'http://crawl.berotato.org/crawl/meta/0.15/logfile',   'http://crawl.berotato.org/crawl/morgue/{name}/morgue-{name}-{end}.txt',           True,  4974258),
        (4004,    cbro,    'http://crawl.berotato.org/crawl/meta/0.16/logfile',   'http://crawl.berotato.org/crawl/morgue/{name}/morgue-{name}-{end}.txt',           True,  17165648),
        (4005,    cbro,    'http://crawl.berotato.org/crawl/meta/0.17/logfile',   'http://crawl.berotato.org/crawl/morgue/{name}/morgue-{name}-{end}.txt',           True,  20152628),
        (4006,    cbro,    'http://crawl.berotato.org/crawl/meta/0.18/logfile',   'http://crawl.berotato.org/crawl/morgue/{name}/morgue-{name}-{end}.txt',           True,  0),
        (4006,    cbro,    'http://crawl.berotato.org/crawl/meta/0.19/logfile',   'http://crawl.berotato.org/crawl/morgue/{name}/morgue-{name}-{end}.txt',           True,  0),
        (5000,    cwz,     'http://webzook.net/soup/trunk/logfile',               'http://webzook.net/soup/morgue/trunk/{name}/morgue-{name}-{end}.txt',             True,  103664998),
       #(5001,    cwz,     'http://webzook.net/soup/0.13/logfile',                'http://webzook.net/soup/morgue/0.13/{name}/morgue-{name}-{end}.txt',              True,  0),
       #(5002,    cwz,     'http://webzook.net/soup/0.14/logfile',                'http://webzook.net/soup/morgue/0.14/{name}/morgue-{name}-{end}.txt',              True,  0),
       #(5003,    cwz,     'http://webzook.net/soup/0.15/logfile',                'http://webzook.net/soup/morgue/0.15/{name}/morgue-{name}-{end}.txt',              True,  0),
       #(5004,    cwz,     'http://webzook.net/soup/0.16/logfile',                'http://webzook.net/soup/morgue/0.16/{name}/morgue-{name}-{end}.txt',              True,  0),
        (5005,    cwz,     'http://webzook.net/soup/0.17/logfile',                'http://webzook.net/soup/morgue/0.17/{name}/morgue-{name}-{end}.txt',              True,  5613183),
        (5006,    cwz,     'http://webzook.net/soup/0.18/logfile',                'http://webzook.net/soup/morgue/0.18/{name}/morgue-{name}-{end}.txt',              True,  0),
        (5007,    cwz,     'http://webzook.net/soup/0.19/logfile',                'http://webzook.net/soup/morgue/0.19/{name}/morgue-{name}-{end}.txt',              True,  0),
       #(6000,    lld,     'http://lazy-life.ddo.jp:8080/meta/trunk/logfile',     'http://lazy-life.ddo.jp:8080/morgue/{name}/morgue-{name}-{end}.txt',              True,  0),
       #(6001,    lld,     'http://lazy-life.ddo.jp:8080/meta/0.14/logfile',      'http://lazy-life.ddo.jp:8080/morgue/{name}/morgue-{name}-{end}.txt',              True,  0),
       #(6002,    lld,     'http://lazy-life.ddo.jp:8080/meta/0.15/logfile',      'http://lazy-life.ddo.jp:8080/morgue/{name}/morgue-{name}-{end}.txt',              True,  0),
       #(6003,    lld,     'http://lazy-life.ddo.jp:8080/meta/0.16/logfile',      'http://lazy-life.ddo.jp:8080/morgue/{name}/morgue-{name}-{end}.txt',              True,  0),
       #(6004,    lld,     'http://lazy-life.ddo.jp:8080/meta/0.17/logfile',      'http://lazy-life.ddo.jp:8080/morgue/{name}/morgue-{name}-{end}.txt',              True,  0),
        (7000,    cxc,     'http://crawl.xtahua.com/crawl/meta/git/logfile',      'http://crawl.xtahua.com/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  45699790),
        (7001,    cxc,     'http://crawl.xtahua.com/crawl/meta/0.14/logfile',     'http://crawl.xtahua.com/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  295987),
        (7002,    cxc,     'http://crawl.xtahua.com/crawl/meta/0.15/logfile',     'http://crawl.xtahua.com/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  1346634),
        (7003,    cxc,     'http://crawl.xtahua.com/crawl/meta/0.16/logfile',     'http://crawl.xtahua.com/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  9592324),
        (7004,    cxc,     'http://crawl.xtahua.com/crawl/meta/0.17/logfile',     'http://crawl.xtahua.com/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  13313271),
        (7005,    cxc,     'http://crawl.xtahua.com/crawl/meta/0.18/logfile',     'http://crawl.xtahua.com/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  0),
        (7006,    cxc,     'http://crawl.xtahua.com/crawl/meta/0.19/logfile',     'http://crawl.xtahua.com/crawl/morgue/{name}/morgue-{name}-{end}.txt',             True,  0),
       #(8000,    cpo,     'https://crawl.project357.org/dcss-logfiles-trunk',    'http://crawl.project357.org/morgue/{name}/morgue-{name}-{end}.txt',               True,  0),
       #(8001,    cpo,     'https://crawl.project357.org/dcss-logfiles-0.15',     'http://crawl.project357.org/morgue/{name}/morgue-{name}-{end}.txt',               True,  0),
       #(8002,    cpo,     'https://crawl.project357.org/dcss-logfiles-0.16',     'http://crawl.project357.org/morgue/{name}/morgue-{name}-{end}.txt',               True,  0),
       #(8003,    cpo,     'https://crawl.project357.org/dcss-logfiles-0.17',     'http://crawl.project357.org/morgue/{name}/morgue-{name}-{end}.txt',               True,  0),
        (9000,     cjr,     'https://crawl.jorgrun.rocks/meta/git/logfile',        'http://crawl.jorgrun.rocks/morgue/{name}/morgue-{name}-{end}.txt',                True,  0),
        (9001,     cjr,     'https://crawl.jorgrun.rocks/meta/0.17/logfile',       'http://crawl.jorgrun.rocks/morgue/{name}/morgue-{name}-{end}.txt',                True,  0),
        (9002,     cjr,     'https://crawl.jorgrun.rocks/meta/0.18/logfile',       'http://crawl.jorgrun.rocks/morgue/{name}/morgue-{name}-{end}.txt',                True,  0),
        (9003,     cjr,     'https://crawl.jorgrun.rocks/meta/0.19/logfile',       'http://crawl.jorgrun.rocks/morgue/{name}/morgue-{name}-{end}.txt',                True,  0),
    ]]
    s.commit()
