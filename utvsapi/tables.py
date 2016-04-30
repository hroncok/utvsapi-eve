from eve.utils import config
from eve_sqlalchemy.decorators import registerSchema
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime

from utvsapi.auth import EnrollmentsAuth

Base = declarative_base()
domain = {}
classes = {}
config.ID_FIELD = config.ITEM_LOOKUP_FIELD = 'id'


def register(cls):
    '''Decorator that registers it and keeps track of it'''
    plural = cls.__name__.lower() + 's'
    registerSchema(plural)(cls)
    domain[plural] = cls._eve_schema[plural]

    # make sure id is our id_field
    # I think this should happen automatically but it doesn't
    domain[plural]['id_field'] = config.ID_FIELD

    domain[plural]['description'] = {'general': cls.__name__ + 's'}
    if cls.__doc__:
        domain[plural]['description'].update({'methods': {'GET': cls.__doc__}})

    # make all ids of type objectid
    # should not be necceassry, but feels good :)
    domain[plural]['schema']['id']['type'] = 'objectid'

    # change data_relation's schema a bit
    for field, value in domain[plural]['schema'].items():
        # is it a field with data_relation
        if 'data_relation' in value:
            # resource is the table name by default
            # eve-sqlalchemy juts hopes it will be the same
            # since we rename things, we need to rename it here as well
            # fortunately, we are consistent and can construct it
            value['data_relation']['resource'] = field + 's'
            # make it embeddable, cannot enable it globally
            value['data_relation']['embeddable'] = True

    if hasattr(cls, '__authentication__'):
        domain[plural]['authentication'] = cls.__authentication__

    if hasattr(cls, '__auth_field__'):
        domain[plural]['auth_field'] = cls.__auth_field__

    if hasattr(cls, '__additional_lookup__'):
        domain[plural]['additional_lookup'] = cls.__additional_lookup__

    classes[plural] = cls
    return cls


def make_links(response, *args):
    for arg in args:
        response[config.LINKS][arg] = {
            'href': '{}s/{}'.format(arg, response[arg]),
            'title': arg.title()
        }


def make_ints(response, *args):
    for arg in args:
        response[arg] = int(response[arg])


@register
class Destination(Base):
    __tablename__ = 'v_destination'

    id = Column('id_destination', Integer, primary_key=True)
    name = Column(String)
    url = Column(String)


@register
class Hall(Base):
    __tablename__ = 'v_hall'

    id = Column('id_hall', Integer, primary_key=True)
    name = Column(String)
    url = Column(String)


@register
class Teacher(Base):
    __tablename__ = 'v_lectors'

    id = Column('id_lector', Integer, primary_key=True)
    degrees_before = Column('title_before', String)
    first_name = Column('name', String)
    last_name = Column('surname', String)
    degrees_after = Column('title_behind', String)
    personal_number = Column('pers_number', Integer)
    url = Column(String)

    def __display_func__(response):
        make_ints(response, 'personal_number')


@register
class Sport(Base):
    __tablename__ = 'v_sports'

    id = Column('id_sport', Integer, primary_key=True)
    shortcut = Column('short', String, unique=True)
    name = Column('sport', String)
    description = Column(String)

    __additional_lookup__ = {'url': 'regex("[\w]+")',
                             'field': 'shortcut'}


@register
class Course(Base):
    __tablename__ = 'v_subjects'

    id = Column('id_subjects', Integer,
                primary_key=True)
    shortcut = Column(String)
    day = Column(Integer)
    starts_at = Column('begin', String)
    ends_at = Column('end', String)
    notice = Column(String)
    semester = Column(Integer)
    sport = Column('sport', Integer,
                   ForeignKey('v_sports.id_sport'))
    hall = Column('hall', Integer, ForeignKey('v_hall.id_hall'))
    teacher = Column('lector', Integer,
                     ForeignKey('v_lectors.id_lector'))

    def __display_func__(response):
        make_ints(response, 'day', 'hall', 'sport', 'teacher')
        make_links(response, 'hall', 'sport', 'teacher')


@register
class Enrollment(Base):
    __tablename__ = 'v_students'
    __authentication__ = EnrollmentsAuth
    __auth_field__ = 'personal_number'

    id = Column('id_student', Integer, primary_key=True)
    personal_number = Column(Integer)
    kos_course_code = Column('kos_kod', String)
    semester = Column(String)
    registration_date = Column(DateTime)
    tour = Column(Boolean)
    kos_code_flag = Column('kos_code', Boolean)
    course = Column('utvs', Integer,
                    ForeignKey('v_subjects.id_subjects'))

    def __display_func__(response):
        if not response['kos_code_flag']:
            response['kos_course_code'] = None
        del response['kos_code_flag']
        make_links(response, 'course')


def remove_dates(response):
    del response[config.LAST_UPDATED]
    del response[config.DATE_CREATED]


def on_fetched_item(resource, response):
    remove_dates(response)
    if hasattr(classes[resource], '__display_func__'):
        return classes[resource].__display_func__(response)


def on_fetched_resource(resource, response):
    for item in response['_items']:
        remove_dates(item)
        if hasattr(classes[resource], '__display_func__'):
            classes[resource].__display_func__(item)
