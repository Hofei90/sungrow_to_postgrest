from peewee import *
import pathlib

SKRIPTPFAD = pathlib.Path(__file__).parent

DBPFAD = SKRIPTPFAD / "datasql.db"
database = SqliteDatabase(DBPFAD)

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Datapoints(BaseModel):
    name = TextField(null=True)
    type = IntegerField(null=True)

    class Meta:
        table_name = 'datapoints'

class Sources(BaseModel):
    name = TextField(null=True)

    class Meta:
        table_name = 'sources'

class SqliteSequence(BaseModel):
    name = BareField(null=True)
    seq = BareField(null=True)

    class Meta:
        table_name = 'sqlite_sequence'
        primary_key = False

class TsBool(BaseModel):
    _from = IntegerField(null=True)
    ack = BooleanField(null=True)
    id = IntegerField(null=True)
    q = IntegerField(null=True)
    ts = IntegerField(null=True)
    val = BooleanField(null=True)

    class Meta:
        table_name = 'ts_bool'
        indexes = (
            (('id', 'ts'), True),
        )
        primary_key = CompositeKey('id', 'ts')

class TsCounter(BaseModel):
    id = IntegerField(null=True)
    ts = IntegerField(null=True)
    val = FloatField(null=True)

    class Meta:
        table_name = 'ts_counter'
        indexes = (
            (('id', 'ts'), True),
        )
        primary_key = CompositeKey('id', 'ts')

class TsNumber(BaseModel):
    _from = IntegerField(null=True)
    ack = BooleanField(null=True)
    id = IntegerField(null=True)
    q = IntegerField(null=True)
    ts = IntegerField(null=True)
    val = FloatField(null=True)

    class Meta:
        table_name = 'ts_number'
        indexes = (
            (('id', 'ts'), True),
        )
        primary_key = CompositeKey('id', 'ts')

class TsString(BaseModel):
    _from = IntegerField(null=True)
    ack = BooleanField(null=True)
    id = IntegerField(null=True)
    q = IntegerField(null=True)
    ts = IntegerField(null=True)
    val = TextField(null=True)

    class Meta:
        table_name = 'ts_string'
        indexes = (
            (('id', 'ts'), True),
        )
        primary_key = CompositeKey('id', 'ts')

