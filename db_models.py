from peewee import *
import datetime

from playhouse.postgres_ext import PostgresqlExtDatabase

from src.config import LOCAL_DB, REMOTE_DB_USER, REMOTE_DB_PASS, REMOTE_DB_NAME, REMOTE_DB_HOST, REMOTE_DB_PORT, \
    LOCAL_DB_PATH

db = SqliteDatabase(LOCAL_DB_PATH) if LOCAL_DB \
    else PostgresqlExtDatabase(REMOTE_DB_NAME, user=REMOTE_DB_USER,
                               password=REMOTE_DB_PASS, host=REMOTE_DB_HOST, port=REMOTE_DB_PORT, autorollback=True)


class BaseModel(Model):
    class Meta:
        database = db


class CompanyDB(BaseModel):
    name = CharField(null=True, unique=False)
    domain = CharField(null=True, unique=False)
    site = CharField(null=True, unique=False)
    industry = CharField(null=True, unique=False)
    industry_code = CharField(null=True, unique=False)
    size = CharField(null=True, unique=False)
    size_codes = CharField(null=True, unique=False)
    actual_employees_num = IntegerField(null=True, unique=False)
    actual_decision_makers_num = IntegerField(null=True, unique=False)
    linkedin_url = CharField(null=True, unique=False)
    location = CharField(null=True, unique=False)
    search_url = CharField(null=True, unique=False)
    status = CharField(null=True, unique=False)
    search_page_num = IntegerField(null=True, unique=False)
    search_num_on_page = IntegerField(null=True, unique=False)
    country = CharField(null=True, unique=False)
    location_codes = CharField(null=True, unique=False)
    linkedin_id = CharField(null=True, unique=False)
    url = CharField(null=True, unique=False)
    created_date = DateTimeField(default=datetime.datetime.now)
    desc = TextField(null=True)


class UserDB(BaseModel):
    fullname = CharField(null=True, unique=False)
    notes = CharField(null=True, unique=False)
    first_name = CharField(null=True, unique=False)
    last_name = CharField(null=True, unique=False)
    title = CharField(null=True, unique=False)
    connection_level = IntegerField(null=True, unique=False)
    director_type = CharField(null=True, unique=False)
    salesnav_url = CharField(null=True, unique=False)
    linkedin_url = CharField(null=True, unique=False)
    status = CharField(null=True, unique=False)
    next_contact_period_days = IntegerField(null=True, unique=False)
    last_contact_date = DateTimeField(null=True)
    sheet_id = CharField(null=True, unique=False)
    sheet_name = CharField(null=True, unique=False)
    created_date = DateTimeField(default=datetime.datetime.now)
    email_verified_by_open = CharField(null=True, unique=False)
    email_verified_by_service = CharField(null=True, unique=False)
    contact_source = CharField(null=True, unique=False)
    company = ForeignKeyField(CompanyDB, backref='users')


class EmailContactDB(BaseModel):
    email = CharField(null=True, unique=False)
    email_validated = BooleanField(null=True, unique=False)
    email_validation_type = CharField(null=True, unique=False)
    created_date = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(UserDB, backref='contacts')
    source = CharField(null=True, unique=False)


class MessageDB(BaseModel):
    main_message = BooleanField(null=True)
    source = CharField(null=True, unique=False)
    created_date = DateTimeField(default=datetime.datetime.now)
    uuid = CharField(null=True, unique=True)
    status = CharField(null=True, unique=False)
    content = CharField(null=True, unique=False)
    thread_id = CharField(null=True, unique=False)
    open_date = DateTimeField(null=True)
    open_count = IntegerField(default=0)
    gmail_id = CharField(null=True, unique=False)
    contact_from = ForeignKeyField(null=True, model=EmailContactDB, backref='fromMessages')
    contact_to = ForeignKeyField(EmailContactDB, backref='toMessages')


db.connect()
db.create_tables([UserDB, CompanyDB, EmailContactDB, MessageDB])
db.close()
