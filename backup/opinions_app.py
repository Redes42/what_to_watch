from datetime import datetime
from random import randrange

import csv

import click
from flask import Flask, redirect, render_template, url_for, flash, abort
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, URLField
from wtforms.validators import DataRequired, Length, Optional

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = 'Jdo23edodFappr257g'
app.json.ensure_ascii = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Opinion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    text = db.Column(db.Text, unique=True, nullable=False)
    source = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    added_by = db.Column(db.String(64))


class OpinionForm(FlaskForm):
    title = StringField(
        'Введите название фильма',
        validators=[DataRequired(message='Обязательное поле'),
                    Length(1, 128)]
    )
    added_by = StringField(
        'Автор',
        validators=[DataRequired(message='Обязательное поле'),
                    Length(1, 64)]
    )
    text = TextAreaField(
        'Напишите мнение',
        validators=[DataRequired(message='Обязательное поле')]
    )
    source = URLField(
        'Добавьте ссылку на подробный обзор фильма',
        validators=[Length(1, 256), Optional()]
    )
    submit = SubmitField('Добавить')


@app.route('/')
def index_view():
    quantity = Opinion.query.count()
    if not quantity:
        abort(500)
    offset_value = randrange(quantity)
    opinion = Opinion.query.offset(offset_value).first()
    # Подключить шаблон opinion.html.
    return render_template('opinion.html', opinion=opinion)


@app.errorhandler(404)
def page_not_found(error):
    # При ошибке 404 в качестве ответа вернётся страница, созданная
    # на основе шаблона 404.html и код HTTP-ответа 404.
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    # Ошибка 500 возникает в нештатных ситуациях на сервере.
    # Например, провалилась валидация данных.
    # В таких случаях можно откатить изменения, незафиксированные в БД,
    # чтобы в базу не записалось ничего лишнего.
    db.session.rollback()
    # Пользователю вернётся страница, сгенерированная на основе шаблона 500.html.
    # Этого шаблона пока нет, но сейчас вы его тоже создадите.
    # Пользователь получит и код HTTP-ответа 500.
    return render_template('500.html'), 500


@app.route('/add', methods=['GET', 'POST'])
def add_opinion_view():
    form = OpinionForm()
    # Если ошибок не возникло...
    if form.validate_on_submit():
        text = form.text.data
        # Если в БД уже есть мнение с текстом, который ввёл пользователь...
        if Opinion.query.filter_by(text=text).first() is not None:
            # ...вызвать функцию flash и передать соответствующее сообщение.
            flash('Такое мнение уже было оставлено ранее!')
            # Вернуть пользователя на страницу «Добавить новое мнение».
            return render_template('add_opinion.html', form=form)
        # ...то нужно создать новый экземпляр класса Opinion...
        opinion = Opinion(
            # ...и передать в него данные, полученные из формы.
            title=form.title.data,
            added_by=form.added_by.data,
            text=form.text.data,
            source=form.source.data
        )
        # Затем добавить его в сессию работы с базой данных...
        db.session.add(opinion)
        # ...и зафиксировать изменения.
        db.session.commit()
        # Затем переадресовать пользователя на страницу добавленного мнения.
        return redirect(url_for('opinion_view', id=opinion.id))
    # Если валидация не пройдена - просто отрисовать страницу с формой.
    return render_template('add_opinion.html', form=form)

@app.route('/opinions/<int:id>')
# Параметром указывается имя переменной.
def opinion_view(id):
    # Теперь можно запросить нужный объект по id...
    opinion = Opinion.query.get_or_404(id)  
    # ...и передать его в шаблон (шаблон - тот же, что и для главной страницы).
    return render_template('opinion.html', opinion=opinion)


@app.cli.command('load_opinions')
def load_opinions_command():
    """Функция загрузки мнений в базу данных."""
    # Открыть файл.
    with open('opinions.csv', encoding='utf-8') as f:
        # Создать итерируемый объект, который отображает каждую строку
        # в качестве словаря с ключами из шапки файла.
        reader = csv.DictReader(f)
        # Для подсчёта строк добавить счётчик.
        counter = 0
        for row in reader:
            # Распакованный словарь использовать
            # для создания экземпляра модели Opinion.
            opinion = Opinion(**row)
            # Добавить объект в сессию и закоммитить
            db.session.add(opinion)
            db.session.commit()
            counter += 1
    click.echo(f'Загружено мнений: {counter}')


if __name__ == '__main__':
    app.run()