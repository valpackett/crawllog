import re
import time
from uritemplate import expand
from requests_futures.sessions import FuturesSession
from conf import db
from models import *


re_name = re.compile(r'name=([^:]+)')
re_end  = re.compile(r'end=([^:]+)')
re_end_fix = re.compile(r'(\d{8})(\d{6}).*')


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
