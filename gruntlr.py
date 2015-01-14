from flask import Flask, redirect, url_for, render_template, flash, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin, login_user, logout_user, current_user
from linkedin_wrapper import LinkedInWrapper


SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
SECRET_KEY = ''
LINKEDIN_KEY = ''
LINKEDIN_SECRET = ''
LINKEDIN_CALLBACK = 'http://localhost:5000/authorize/callback'
DEBUG = False

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('GRUNTLR_SETTINGS', silent=True)

db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'index'
linkedin = LinkedInWrapper( app.config['LINKEDIN_KEY'], app.config['LINKEDIN_SECRET'], app.config['LINKEDIN_CALLBACK'])


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    name = db.Column(db.String(64), nullable=False)


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/authorize')
def linkedin_authorize():
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    return linkedin.authorize()

@app.route('/authorize/callback')
def linkedin_callback():
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    social_id, name = linkedin.authorize_callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, name=name)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))

@app.route('/user/companies')
def user_companies():
    if current_user.is_anonymous():
        return redirect(url_for('index'))
    return jsonify(companies=linkedin.get_companies_worked_at())


if __name__ == '__main__':
    db.create_all()
    app.run()
