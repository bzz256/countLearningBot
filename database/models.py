from peewee import *

db = SqliteDatabase('./database/data.sqlite')


class BaseModel(Model):
    class Meta:
        database = db


class Result(BaseModel):
    class Meta:
        db_table = 'result'
    name = CharField(unique=True)
    score = IntegerField()
    answers = IntegerField()
    time = DoubleField()


def create_tables():
    with db:
        db.create_tables([Result])
