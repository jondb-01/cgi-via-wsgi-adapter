"""
UWSGI_ADAPTER_BASEDIR=$(pwd)/apps uwsgi --http=:8080  --wsgi=adapter --touch-reload=apps/test.cgi --touch-reload=adapter.py  --uid=www-data --gid=www-data
"""
import os
import sys
import subprocess


def code(code, start_response):
    start_response(str(code), [('content-type', 'text/html')])
    return "Status code %s." % code

def process_response(resp):
    # Process response
    resp = resp.split('\n')
    data = ''
    headers = []
    status = '200'
    for i, line in enumerate(resp):
        if line == '':
            data = resp[i+1:]
            break
        key, value = line.split(':', 1)
        key = key.lower().strip()
        value = value.strip()
        if key == 'status':
            status = str(value)
            err_buff.write('status: %s\n' % status)
        else:
            headers.append((key, value))
    return status, headers, data

def application(environ, start_response):
    # EVN
    app_env = dict(environ.items())
    del(app_env['wsgi.input'])
    del(app_env['wsgi.errors'])
    for k, v in app_env.items():
        if not isinstance(v, basestring):
            v = str(v)
        os.environ[k] =v

    # I/O
    in_buff = environ['wsgi.input'].read()
    err_buff = environ['wsgi.errors']

    # Find app to launch
    BASEDIR = os.environ['UWSGI_ADAPTER_BASEDIR']
    if BASEDIR[0] != '/':
        raise Exception("Absolute path required for UWSGI_ADAPTER_BASEDIR!")

    PATH = os.environ.get('PATH_INFO').lstrip('/')
    _script_path = os.path.abspath(os.path.join(BASEDIR, PATH))
    err_buff.write("_script_path: %s\n" % (_script_path))
    script_name = None
    if not os.path.exists(_script_path):
        script_name = None
    elif os.path.isfile(_script_path):
        script_name = _script_path
    elif os.path.isdir(_script_path):
        for default in ("index.py", "index.cgi"):
            _script_name = os.path.join(_script_path, default)
            if os.path.exists(_script_name) and os.path.isfile(_script_name):
                script_name = _script_name
                break

    if not script_name:
        code(404, start_response)
        return "File not found.\n%s" % _script_path

    script_filename, script_ext = os.path.splitext(script_name)
    if script_ext not in ('.cgi', '.py'):
        code(403, start_response)
        return "Execution not allowed."
    
    assert script_name[:len(BASEDIR)] == BASEDIR, script_name + ' ' + BASEDIR
    
    # Launch
    os.chdir(os.path.dirname(script_name))
    ps = subprocess.Popen([script_name], 
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    (resp, stderrdata) = ps.communicate(input=in_buff)
    ret_code = ps.wait()

    # Handle errors
    for errdata in stderrdata.split("\n"):
        if errdata:
            err_buff.write("stderr(%s): " % script_name)
            err_buff.write(errdata)
            err_buff.write("\n")

    if ret_code != 0:
        if resp:
            status, headers, data = process_response(resp)
            start_response('500', headers)
            return data
        else:
            start_response('500', [('Content-type', 'text/plain')])
            return "Internal Server Error. Info:\n%s\n%s" % (stderrdata, resp)

    # Process response
    status, headers, data = process_response(resp)
    start_response(status, headers)
    data = "\n".join(data)
    return [data]

