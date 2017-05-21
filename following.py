#!/usr/bin/env python
import re
import gc
import time
import logging
from uritemplate import expand
from requests_futures.sessions import FuturesSession
from models import *
from processing import process_log

logging.basicConfig(level=logging.INFO)
Session = my_sessionmaker()

def parse_xlogfile(line):
    result = {}
    for (k, v) in [kv.split('=') for kv in line.replace('::', '\n').split(':')]:
        result[k.replace('\n', ':')] = v.replace('\n', ':')
    return result


re_end_fix = re.compile(r'(\d{8})(\d{6}).*')
def crawl_fixed_end(end):
    # Why the hell do Crawl months start at zero?
    end = re_end_fix.sub(r'\1-\2', end)
    return end[:4] + str(int(end[4:6]) + 1).zfill(2) + end[6:]


def follow_logs():
    http = FuturesSession()
    while True:
        try:
            actually_follow_logs(http)
        except Exception as e:
            print(e)
        gc.collect()
        time.sleep(60)

def actually_follow_logs(http):
    logging.info('Starting update')
    s = Session()
    logs = s.query(ServerLog).all()
    logging.info('Requesting %s logs' % len(logs))
    head_reqs = [http.head(log.uri) for log in logs]
    logs_to_get = [(log, req.result().headers['Content-Length'])
                   for log, req in zip(logs, head_reqs)
                   if int(req.result().headers['Content-Length']) > log.position]
    for log, new_len in logs_to_get:
        logging.info('%s now available bytes=%s-%s' % (log.uri, log.position, new_len))
    get_reqs = [http.get(log.uri, stream=True, headers={
                    'range': 'bytes=%s-%s' % (log.position, new_len)
                }) for log, new_len in logs_to_get]
    for (log, _), req in zip(logs_to_get, get_reqs):
        resp = req.result()
        if resp.status_code != 206:
            logging.warning('%s status: %s' % (log.uri, resp.status_code))
            continue
        logging.info('%s reading' % log.uri)
        log.position += int(resp.headers['Content-Length'])
        for line in resp.iter_lines():
            if not line:
                continue
            line = line.decode('utf-8', errors='replace')
            data = {}
            try:
                data = parse_xlogfile(line)
                if log.crawl_month_fix:
                    data['end'] = crawl_fixed_end(data['end'])
            except:
                logging.warning('could not parse log entry: %s' % line)
                continue
            account = s.query(UserOnServer).filter_by(server=log.server, name=data['name']).first()
            if not account:
                logging.info('no account found for %s on server %s' % (data['name'], log.server.name))
                continue
            log_uri = expand(log.uri_template, data)
            text = http.get(log_uri).result().text
            process_log(text, account.user, uri=log_uri, respect_threshold=True)
        logging.info('%s now at byte %s' % (log.uri, log.position))
        s.add(log)
    s.commit()

if __name__ == "__main__":
    follow_logs()
