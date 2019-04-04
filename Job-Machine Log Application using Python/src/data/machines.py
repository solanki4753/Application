import datetime
import mongoengine

from data.bookings import Booking


class Machine(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    name = mongoengine.StringField(required=True)
    price = mongoengine.FloatField(required=True)
    square_meters = mongoengine.FloatField(required=True)
    
    #safety feature
    is_carpeted = mongoengine.BooleanField(required=True)

    #cooler
    has_toys = mongoengine.BooleanField(required=True)
    
    #certied_worker needed
    allow_dangerous_snakes = mongoengine.BooleanField(default=False)

    bookings = mongoengine.EmbeddedDocumentListField(Booking)

    meta = {
        'db_alias': 'core',
        'collection': 'machines'
    }
