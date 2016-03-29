import requests


def process_log(text, user, respect_threshold=False):
    print(text)
    print(user)
    summary = '\n\n'.join(text.split('\n\n')[:3])
    post_micropub('<pre class="crawllog-log crawllog-summary">%s</pre>' % summary,
                  '<pre class="crawllog-log crawllog-full">%s</pre>' % text,
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
