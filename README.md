cgi-via-wsgi-adapter
====================

Wraps a CGI script in a WSGI container to run with uWSGI.

There are a bunch of scripts to serve wsgi through a CGI web server. This solves a different problem.

Nginx doesn't support cgi. Instead it takes the model that the web server terminates client connections, and routes to web applications on the back end. CGI is a web application. uWSGI with emperor is a fantastic way to run WSGI applications. This script sits between uWSGI and your CGI script.

        [CLIENT-REQUEST] --(http)--> [NGINX] --(uWSGI)--> [uWSGI] --(wsgi)--> [cgi-via-wsgi-adapter] --(CGI)--> [the_cgi_app]

Names within parenthesis denote protocols.  Brackets denote applications/servers.

The git repository has a sample app running under /apps/test.cgi and the uwsgi.ini is configured to run http on port 8080. The following diagram:

        [CLIENT-REQUEST] --(http)-----------------------> [uWSGI] --(wsgi)--> [cgi-via-wsgi-adapter] --(CGI)--> [the_cgi_app]

The adapter searches for the CGI file by appending the client supplied path to the environment variable UWSGI_ADAPTER_BASEDIR which is configured in uwsgi.ini. The default search path is /[cwd]/apps/[uri-path].

The following will start the included test app.

```
git clone git@github.com:jondb/cgi-via-wsgi-adapter.git
cd cgi-via-wsgi-adapter
virtualenv .
source bin/activate
pip install uwsgi
uwsgi uwsgi.ini
```

Then point your browser at http://localhost:8080/?headers=1&name=me
http://localhost:8080/test

For a production config,

not there yet.









