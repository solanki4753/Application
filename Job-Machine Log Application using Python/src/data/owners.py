import datetime
import mongoengine


class Owner(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    name = mongoengine.StringField(required=True)
    email = mongoengine.StringField(required=True)

    job_ids = mongoengine.ListField()
    machine_ids = mongoengine.ListField()

    meta = {
        'db_alias': 'core',
        'collection': 'owners'
    }
