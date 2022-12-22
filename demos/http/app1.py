import os
try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from jinja2 import escape
from jinja2.utils import generate_lorem_ipsum
from flask import Flask, make_response, request, redirect, url_for, session, jsonify, abort

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'secret_string')

@app.route('/')
@app.route('/hello')
def hello():
    name = request.args.get('name')
    if name == None:
        name = request.cookies.get('name', 'Human')
    response = '<h1>Hello, %s!</h1>' % escape(name)
    if 'log_in' in session:
        response += '[Authenticated]'
    else:
        response += '[Not Authenticated]'
    return response

@app.route('/hi')
def hi():
    return redirect(url_for('hello'))

@app.route('/goback/<int:year>')
def go_back(year):
    return '<h1>go back %d year!' % (2018 - year)

@app.route('/colors/<any(blue, black, red):color>')
def three_colors(color):
    return '<h1>hello, %s!</h1>' % color

@app.route('/brew/<drink>')
def teapot(drink):
    if drink == 'coffee':
        abort(404)
    else:
        return '<h1>a drop of tea!</h1>'

@app.route('/404')
def not_found():
    abort(404)

@app.route('/note', defaults={'content_type':'text'})
@app.route('/note/<content_type>')
def note(content_type):
    content_type = content_type.lower()
    if content_type == 'text':
        body = '''
        To: Peter
        From: Jane
        heading: Reminder
        body: Don't forget the party!
        '''
        response = make_response(body)
        response.mimetype = 'text/plain'
    elif content_type == 'html':
        body = '''
        <!DOCTYPE HTML>
        <html>
        <head></head>
        <body>
            <h1>Note</h1>
            <p>To: Peter</p>
            <p>From: Jane</p>
            <p>heading: Reminder</p>
            <p>body: Don't forget the party!</p>
        </body>
        </html>
        '''
        response = make_response(body)
        response.mimetype = 'text/html'
    elif content_type == 'json':
        body = {"note": {
            "to": "Peter",
            "from": "Jane",
            "heading": "Remider",
            "body": "Don't forget the party!"
        }
        }
        response = jsonify(body)
    else:
        abort(404)
    return response

@app.route('/set/<name>')
def set_cookie(name):
    response = make_response(redirect(url_for('hello')))
    response.set_cookie('name', name)
    return response

@app.route('/login')
def login():
    session['log_in'] = True
    return redirect(url_for('hello'))

@app.route('/logout')
def logout():
    if 'log_in' in session:
        session.pop('log_in')
    return redirect(url_for('hello'))

@app.route('/admin')
def admin():
    if 'log_in' not in session:
        abort(403)
    else:
        return 'welcome to admin page'

@app.route('/post')
def show_post():
    post_body = generate_lorem_ipsum(n=2)
    return '''
<h1>A very long post</h1>
<div class="body">%s</div>
<button id="load">Load More</button>
<script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
<script type="text/javascript">
$(function() {
    $('#load').click(function() {
        $.ajax({
            url: '/more',
            type: 'get',
            success: function(data){
                $('.body').append(data);
            }
        })
    })
})
</script>''' % post_body

@app.route('/more')
def load_post():
    return generate_lorem_ipsum(n=1)

@app.route('/foo')
def foo():
    return '<h1>foo page<a href="%s">do something and redirect</a>' \
           % url_for('do_somethin', next=request.full_path)

@app.route('/bar')
def bar():
    return '<h1>bar page<a href="%s">do something and redirect</a>' \
        % url_for('do_something', next=request.full_path)

@app.route('/do-something')
def do_something():
    return redirect_back()

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(ref_url,target))
    return test_url.scheme in ('http','https') and \
        ref_url.netloc == test_url.netloc

def redirect_back(default='hello', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))

