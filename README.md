[![unlicense](https://img.shields.io/badge/un-license-green.svg?style=flat)](https://unlicense.org)

# crawllog

A webapp that posts your [Dungeon Crawl Stone Soup](https://crawl.develz.org/) game logs (morgue files) to your website using [Micropub](https://micropub.net/).

```shell
$ doas pkg install py36-pipenv py37-sqlite3 postgresql11-client
$ pipenv sync
$ export CRAWLLOG_DATABASE_URI=postgresql+psycopg2cffi://localhost/crawllog
$ pipenv run ./manage.py db upgrade
$ pipenv run ./manage.py upsert_content
$ pipenv run ./manage.py runserver # dev server
$ pipenv run ./following.py # worker process
$ pipenv run uwsgi --wsgi-file app.py --callable app ...
# see conf.py for env variables used
```

## Contributing

Please feel free to submit pull requests!

By participating in this project you agree to follow the [Contributor Code of Conduct](http://contributor-covenant.org/version/1/4/).

## License

This is free and unencumbered software released into the public domain.  
For more information, please refer to the `UNLICENSE` file or [unlicense.org](http://unlicense.org).
