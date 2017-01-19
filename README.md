# crawllog [![unlicense](https://img.shields.io/badge/un-license-green.svg?style=flat)](http://unlicense.org)

A webapp that posts your [Dungeon Crawl Stone Soup](http://crawl.develz.org/) game logs (morgue files) to your website using [Micropub](http://micropub.net/).

```bash
$ python3.6 -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
$ export CRAWLLOG_DATABASE_URI=postgres://localhost/crawllog
$ ./manage.py db upgrade
$ ./manage.py upsert_content
$ ./manage.py runserver # dev server
$ ./following.py # worker process
$ uwsgi --wsgi-file app.py --callable app ...
# see conf.py for env variables used
```

## Contributing

Please feel free to submit pull requests!

By participating in this project you agree to follow the [Contributor Code of Conduct](http://contributor-covenant.org/version/1/4/).

## License

This is free and unencumbered software released into the public domain.  
For more information, please refer to the `UNLICENSE` file or [unlicense.org](http://unlicense.org).
