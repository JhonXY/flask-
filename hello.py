# coding=utf-8
from flask import *
from flask_script import Manager, Shell
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.route('/', methods=['GET', 'POST'])  # 操作数据库
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'),
                           known=session.get('known', False), current_time=datetime.utcnow())

'''
@app.route('/', methods=['GET', 'POST'])
def index():
    # name = None
    form = NameForm()  # 实例化form
    if form.validate_on_submit():   # 验证是否有值

        方案一，刷新会要求重新提交表单
            name = form.name.data  # 赋值给局部变量
            form.name.data = ''  # 清空列表
        return render_template('index.html', current_time=datetime.utcnow(), form=form, name=name)
        # 传值给jinjia2模板变量，render_template进行模板渲染

        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:  # 提交名与存储在用户会话中的名字进行比较
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data  # 将数据存储在用户对话中
        return redirect(url_for('index'))  # 生成http重定向响应
    return render_template('index.html', current_time=datetime.utcnow(), form=form, name=session.get('name'))
'''


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', current_time=datetime.utcnow(), name=name)


@app.errorhandler(404)  # 设置错误页面
def page_not_found(e):
    return render_template('404.html', current_time=datetime.utcnow()), 404


@app.errorhandler(500)
def inter_server_error(e):
    return render_template('500.html'), 500


class NameForm(FlaskForm):  # 定义表单类
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == '__main__':
    # app.run(debug=True)
    manager.run()

