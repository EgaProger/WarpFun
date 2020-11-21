from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from django.core.validators import URLValidator
from validate_email import validate_email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import string
from random import choice

letters = list(string.ascii_letters) + list(string.digits)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
db = SQLAlchemy(app)


class Link(db.Model):
    '''Поле для одной ссылки в таблице'''
    id = db.Column(db.Integer, primary_key=True)
    origin_link = db.Column(db.Text, nullable=False)
    short_link = db.Column(db.Text, nullable=False)
    clicks = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return 'Link %r>' % self.id


class AccessKey(db.Model):
    '''Поле для ключа доступа в таблице'''
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return 'AccessKey %r>' % self.id


class Email(db.Model):
    '''Поле для электронной почты в таблице в таблице'''
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return 'Email %r>' % self.id


def generateAccessKey():
    '''Генерация ключа доступа'''
    access_key = []
    for i in range(0, 10):
        access_key.append(choice(letters))

    return "".join(access_key)


def send_email(sent_to):
    '''Отправка письма на эл. почту'''
    access_key = generateAccessKey()
    accesskey = AccessKey(key=access_key)
    db.session.add(accesskey)
    db.session.commit()
    sent_from = 'warplink.api@gmail.com'
    message = MIMEMultipart("alternative")
    message["Subject"] = "AccessKey на WarpLink"
    message["From"] = sent_from
    message["To"] = sent_to

    html = '''
    <html>
      <body>
        <div style='font-size: 30px;text-align:center;'>
            Здравствуйте!<br>
            Вы запрашивали код для получения доступа к WarpLink API<br>
            Ваш код: <span style="color:green;">{}</span><br>
            Инструкция пользования WarpLink API, достуна по <a href="warp.fun/api/">ссылке</a>. <br>
            С наилучшими пожеланиями, <a href='warp.fun'>WarpLink</a>. <br>
            <img src="https://warp.fun/static/img/favicon.png" height="48" width="48" alt="">
        </div>
      </body>
    </html>
    '''.format(access_key)

    msg = MIMEText(html, "html")
    message.attach(msg)

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(sent_from, 'password') # invalid password
    server.sendmail(sent_from, sent_to, message.as_string())
    server.close()


validate = URLValidator()


def generateShortLink():
    '''Генерация сокращенной ссылки'''
    short_url = []
    for i in range(0, 6):
        short_url.append(choice(letters))

    return "".join(short_url)


def gen():
    '''Говнокод'''
    short_url = generateShortLink()
    query = Link.query.filter_by(short_link=short_url).first()
    if query is None or query != short_url:
        return short_url

    else:
        gen()

    return short_url


@app.route('/api/create/accesskey=<string:YOUR_ACCESS_KEY>;originlink=<string:YOUR_ORIGIN_LINK>/')
def API_createShortLink(YOUR_ACCESS_KEY, YOUR_ORIGIN_LINK):
    try:
        query = AccessKey.query.filter_by(key=YOUR_ACCESS_KEY).first()
        if YOUR_ACCESS_KEY == query.key:
            short_url = gen()
            if validate('http://' + YOUR_ORIGIN_LINK):
                link = Link(origin_link=YOUR_ORIGIN_LINK, short_link=short_url, clicks=0)
                db.session.add(link)
                db.session.commit()
                return 'warp.fun/' + short_url

            else:
                return "InvalidUrl"

        else:
            return 'Invalid AccessKey'

    except:
        return 'Invalid AccessKey'


@app.route('/api/clicks/accesskey=<string:YOUR_ACCESS_KEY>;shortlink=<string:YOUR_SHORT_LINK>/')
def API_clicks(YOUR_ACCESS_KEY, YOUR_SHORT_LINK):
    query = AccessKey.query.filter_by(key=YOUR_ACCESS_KEY).first()
    if YOUR_ACCESS_KEY == query.key:
        query = Link.query.filter_by(short_link=YOUR_SHORT_LINK).first()
        if query.short_link != None:
            return '{}'.format(query.clicks)

        else:
            return 'InvalidUrl'

    else:
        return 'Invalid AccessKey'


@app.route('/<string:short_link>/')
def redirect_from_short_link(short_link):
    short_url = Link.query.filter_by(short_link=short_link).first()
    try:
        if short_url.short_link != None:
            new_link = Link(origin_link=short_url.origin_link, short_link=short_url.short_link,
                            clicks=short_url.clicks + 1)
            url = short_url.origin_link
            db.session.delete(short_url)
            db.session.add(new_link)
            db.session.commit()
            if 'http' in url:
                return redirect(url)

            else:
                return redirect('http://' + url)

        else:
            return redirect('/fail/')

    except:
        return 'Invalid AccessKey'


@app.route('/<string:short_link>*/')
def get_clicks(short_link):
    try:
        short_url = Link.query.filter_by(short_link=short_link).first()
        if short_url.short_link != None:
            return render_template('clicks.html', clicks=short_url.clicks,
                                   link='https://warp.fun/' + short_url.short_link)

        else:
            return redirect('/invalid-link/')

    except:
        return redirect('/invalid-link/')


@app.route('/success/<string:short_link>/')
def success_in_create_link(short_link):
    return render_template('success.html', url='warp.fun/' + short_link)


@app.route('/about-author/')
def about():
    return render_template('about-author.html')


@app.route('/invalid-link/')
def invalid_link():
    return render_template('no_short_link.html')


@app.route('/api/get-access-key/', methods=['POST', 'GET'])
def get_key():
    if request.method == 'POST':
        email = request.form['email']
        if validate_email(email):
            try:
                send_email(email)

            except:
                return render_template('accesskey.html', status='Письмо не было отправлено', readonly='readonly',
                                       href='api-get-code', btn_value='Повторить попытку')

            return render_template('accesskey.html', status='Письмо было отправлено', readonly='readonly',
                                   href='api-nav', btn_value='Успешно')

    else:
        return render_template('accesskey.html',
                               status_down='На ваш электронный ящик придет письмо с ключом доступа (access key)',
                               href='', btn_value='Отправить')


@app.route('/mailing/', methods=['POST', 'GET'])
def mailing():
    if request.method == 'POST':
        email = request.form['email']
        email = Email(email=email)
        try:
            db.session.add(email)
            db.session.commit()

        except:
            pass

        return redirect('/mail_success/')


    else:
        return render_template('mailing.html')


@app.route('/mail-success/')
def mail_success():
    return render_template('mail_success.html')


@app.route('/dev/')
def dev():
    return render_template('dev.html')


@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        try:
            url = request.form['url']
            if 'http' not in url:
                validate('http://' + url)

            else:
                validate(url)

            short_url = gen()
            link = Link(origin_link=url, short_link=short_url, clicks=0)
            try:
                db.session.add(link)
                db.session.commit()
                return redirect('/success/' + short_url + '/')

            except:
                return "An error occurred"

        except:
            try:
                email = request.form['email']
                email = Email(email=email)
                try:
                    db.session.add(email)
                    db.session.commit()
                    return redirect('/mail-success/')

                except:
                    return redirect('/invalid-link/')

            except:
                return redirect('/invalid-link/')

    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
