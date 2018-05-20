## pymgur

### A pastebin for images

pymgur is a tool that allow posting images on a local instance
and serve them afterwards (analog to [pastebin](https://github.com/lordelph/pastebin))

It's designed so that anyone can run his own instance relatively easily,
and to allow you to easily post images via curl


Requirements are:

- python 3
- [flask](http://flask.pocoo.org/) (web framework)
- [pillow](https://github.com/python-pillow/Pillow) (image library)

Images are stored locally on the filesystem and image metadata is stored in a sqlite database


A demo site is available at http://pymgur.chivil.com/


Current version should he usable without too much hassle


### API use (posting)

TLDR: `curl -F img=@animage.jpg http://localhost:5000`

(TODO, document options) 


### Installation

#### Using virtualenv

pymgur can run inside a virtualenv simply by running the setup script

`python setup.py install`

That will install the dependencies and create a `pymgur` executable that you
can use to run a local server


#### Using system packages

Since there is only 2 dependencies, you can simply install them from your distribution,
for example using apt-get install python3-flask python3-pil on Debian/Ubuntu

You can then run the server using `python pymgur/` (pymgur being the directory
containing the local python files)


### Configuration

The default configuration is [pymgur.default.ini](pymgur.default.ini) and
should be appropriately documented.

Modifying it should work, but you'd probably be better off by making a copy,
modify the values you want, and reference it when running pymgur.

You can point to a specific configuration file by:

- using the `-c` option when running a server (for example `pymgur -c /etc/pymgur.ini`)
- using the `$PYMGUR_CONFIG` environment variable (for example `export PYMGUR_CONFIG=/etc/pymgur.ini`)

By default the local server will only listen to the local interface (127.0.0.1) on port 5000,
you can change that by modifying the **SERVER_NAME** in the configuration.

By default the data directory is located with the libraries (in [pymgur/data/](pymgur/data/))
which sounds sane but it not a practical default.


### Execution

You can run the standalone server locally with the `pymgur` command, this works
for testing out the application but it not really recommended to use it daily

Instead you should use it as a WSGI application (ideally behind an actual
web server like nginx), for example with uwsgi:

`PYMGUR_CONFIG=/etc/pymgur.ini uwsgi -H myvirtualenv --http :9090 -T -w pymgur`

The application is currently designed to run properly with threads