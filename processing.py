import re
import requests


re_crawl_version = re.compile(r'^\s*(?P<game>.+) version (?P<version>[^\s]+)\s+\((?P<interface>[^)]+)\) character file.', flags=re.MULTILINE)
p_crawl_version  = lambda x: re_crawl_version.sub(' <span class="p-game h-x-app"><span class="p-name">\g<game></span> version <span class="p-version">\g<version></span> (<span class="p-x-ui-variant">\g<interface></span>)</span> character file.', x)

re_crawl_score = re.compile(r'^(?P<score>\d+) (?P<name>.+) the (?P<title>.+) \(level (?P<level>\d+)', flags=re.MULTILINE)
p_crawl_score  = lambda x: re_crawl_score.sub('<span class="p-score">\g<score></span> <span class="p-character-name">\g<name></span> the <span class="p-character-title">\g<title></span> (level <span class="p-character-level">\g<level></span>', x)

re_crawl_time = re.compile(r'The game lasted (?P<time>[^\s]+) \((?P<turns>[^\s]+) turns\)')
p_crawl_time  = lambda x: re_crawl_time.sub('The game lasted <span class="p-time">\g<time></span> (<span class="p-turns">\g<turns></span> turns)', x)

re_crawl_victory = re.compile(r'... and (?P<runes>\d+) runes')
p_crawl_victory  = lambda x: re_crawl_victory.sub('... and <span class="p-runes">\g<runes></span> runes', x)


def process_log(text, user, respect_threshold=False):
    text = p_crawl_version(text)
    text = p_crawl_score(text)
    text = p_crawl_time(text)
    text = p_crawl_victory(text)
    summary = '\n\n'.join(text.split('\n\n')[:3])
    return post_micropub(
        '<pre class="crawllog-log crawllog-summary p-x-game-log h-x-game-log">%s</pre>' % summary,
        '<pre class="crawllog-log crawllog-full p-x-game-log h-x-game-log">%s</pre>' % text,
        user)


def post_micropub(summary, content, user):
    return requests.post(user.micropub_uri, headers={
        'Authorization': 'Bearer %s' % user.access_token
    }, json={
        'type': ['h-entry'],
        'properties': {
            'summary': [
                {
                    'html': summary
                }
            ],
            'content': [
                {
                    'html': content
                }
            ]
        }
    })
