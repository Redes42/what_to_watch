# what_to_watch/opinions_app/api_views.py
from random import randrange

from flask import jsonify, request

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import Opinion
from .views import random_opinion


@app.route('/api/opinions/<int:id>/', methods=('GET',))
def get_opinion(id):
    opinion = Opinion.query.get_or_404(id)
    # Никаких лишних функций, просто метод to_dict().
    return jsonify({'opinion': opinion.to_dict()}), 200


@app.route('/api/opinions/<int:id>/', methods=('PATCH',))
def update_opinion(id):
    data = request.get_json()
    # Если метод get_or_404 не найдёт указанный ID,
    # он выбросит исключение 404:
    opinion = Opinion.query.get(id)
    if opinion is None:
        raise InvalidAPIUsage('В базе данных нет мнений', 404)
    if(
        'title' in data and
        Opinion.query.filter_by(text=data['text']).first() is not None
    ):
        # Выбросить собственное исключение.
        raise InvalidAPIUsage('Такое мнение уже есть в базе данных')
    for key in data:
        opinion.__setattr__(key, data.get(key, opinion.__getattribute__(key)))
    # opinion.title = data.get('title', opinion.title)
    # opinion.text = data.get('text', opinion.text)
    # opinion.source = data.get('source', opinion.source)
    # opinion.added_by = data.get('added_by', opinion.added_by)
    # Все изменения нужно сохранить в базе данных.
    # Объект opinion добавлять в сессию не нужно.
    # Этот объект получен из БД методом get_or_404() и уже хранится в сессии.
    db.session.commit()
    # При изменении объекта нужно вернуть сам объект и код 200.
    return jsonify({'opinion': opinion.to_dict()}), 200


@app.route('/api/opinions/<int:id>/', methods=['DELETE'])
def delete_opinion(id):
    opinion = Opinion.query.get_or_404(id)
    db.session.delete(opinion)
    db.session.commit()
    # При удалении принято возвращать только код ответа 204.
    return '', 204


@app.route('/api/opinions/', methods=['GET'])
def get_opinions():
    # Запросить список объектов.
    opinions = Opinion.query.all()
    # Поочерёдно сериализовать каждый объект,
    # а потом все объекты поместить в список opinions_list.
    opinions_list = [opinion.to_dict() for opinion in opinions]
    return jsonify({'opinions': opinions_list}), 200


@app.route('/api/opinions/', methods=['POST'])
def add_opinion():
    # Получить данные из запроса в виде словаря.
    data = request.get_json()
    if 'title' not in data or 'text' not in data:
        # Выбросить собственное исключение.
        # Второй параметр (статус-код) в этом обработчике можно не передавать:
        # нужно вернуть код 400, а он и так возвращается по умолчанию.
        raise InvalidAPIUsage('В запросе отсутствуют обязательные поля')
    if Opinion.query.filter_by(text=data['text']).first() is not None:
        # Выбросить собственное исключение.
        raise InvalidAPIUsage('Такое мнение уже есть в базе данных')
    opinion = Opinion()
    opinion.from_dict(data)
    db.session.add(opinion)
    db.session.commit()
    return jsonify({'opinion': opinion.to_dict()}), 201

@app.route('/api/get-random-opinion/', methods=['GET'])
def get_random_opinion():
    opinion = random_opinion()
    if opinion is not None:
        return jsonify({'opinion': opinion.to_dict()}), 200
    raise InvalidAPIUsage('В базе данных нет мнений', 404)