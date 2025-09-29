from datetime import datetime

from . import db

class Opinion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    text = db.Column(db.Text, unique=True, nullable=False)
    source = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    added_by = db.Column(db.String(64))

    def to_dict(self):
        return {
            column.name: getattr(
                self, column.name
            )
            for column in self.__table__.columns
        }

    def from_dict(self, data):
        # Для каждого поля модели, которое можно заполнить...
        for field in self.__table__.columns:
            # ...выполнить проверку — есть ли ключ с таким же именем в словаре.
            if field.name in data:
                # Если есть, добавить значение из словаря
                # в соответствующее поле объекта модели.
                setattr(self, field.name, data[field.name])