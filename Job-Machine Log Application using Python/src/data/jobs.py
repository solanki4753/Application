import datetime
import mongoengine


class Job(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    species = mongoengine.StringField(required=True)
	
    length = mongoengine.FloatField(required=True)
    name = mongoengine.StringField(required=True)
    is_venomous = mongoengine.BooleanField(required=True)
    #is_venomous=top priority
    meta = {
        'db_alias': 'core',
        'collection': 'jobs'
    }
