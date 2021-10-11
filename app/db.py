import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import Column, BigInteger, Integer, String

from app import quart_app

engine = sqlalchemy.create_engine(
    'sqlite:///{}'.format(quart_app.config['DATABASE_PATH']),
    convert_unicode=True,
    echo=quart_app.config['DEBUG'])

session = scoped_session(sessionmaker(autocommit=True,
                                      autoflush=True,
                                      bind=engine))

Base = declarative_base()
Base.query = session.query_property()


TERM_CODE = {
    '1-1': 11,
    '1-2': 12,
    '2-1': 21,
    '2-2': 22,
    'summer': 13,
    'winter': 23,
    'other': 30,
    'tokyo ⅰ': 31,
    'tokyo ⅱ': 32,
    'tokyo ⅲ': 33,
    'tokyo ⅳ': 34
}

ADDITIONAL_CODE = {
    'j': 1,
    'e': 2,
    'ej': 3,
    'f': 4,
    'g': 5,
    's': 6
}


def _term_code(term):
    term = term.lower()
    try:
        return TERM_CODE[term]
    except KeyError:
        if 'summer' in term:
            return TERM_CODE['summer']
        elif 'winter' in term:
            return TERM_CODE['winter']
        return TERM_CODE['other']


def _language_code(subject_code):
    subject_code = subject_code.lower()
    if subject_code.startswith('e'):
        return ADDITIONAL_CODE['e']
    elif 'ej' in subject_code[-2:]:
        return ADDITIONAL_CODE['ej']
    else:
        try:
            return ADDITIONAL_CODE[subject_code[-1]]
        except KeyError:
            return ADDITIONAL_CODE['j']


def _subject_id(org: str, year: int, group: str, subject_code: str, term: str):
    if org == 'jaist':
        return int('{0}{1}{2}{3}{4}'.format(year % 100,
                                            _term_code(term),
                                            ord(group.lower()),
                                            ''.join(i for i in subject_code if i.isdigit()),
                                            _language_code(subject_code))
                   )
    else:
        return int('{0}{1}'.format(year % 100, subject_code))


class SyllabusSubjects(Base):
    __tablename__ = 'syllabus_subjects'

    id = Column(BigInteger, primary_key=True)
    year = Column(Integer, nullable=False)
    group = Column(String, nullable=False)
    subject_code = Column(String, nullable=False)
    title = Column(String, nullable=False)
    title_ja = Column(String, nullable=False)
    term = Column(String, nullable=False)
    period = Column(String, nullable=False, default='')
    course_credits = Column(Integer, nullable=False, default=0)
    instructor = Column(String, nullable=False)
    org = Column(String, nullable=False)

    def __init__(self, year: int, group: str, subject_code: str, title: str, title_ja: str,
                 term: str, period: str, course_credits: int, instructor: str, org: str):
        self.year = year
        self.group = group
        self.subject_code = subject_code
        self.title = title
        self.title_ja = title_ja
        self.term = term
        self.period = period
        self.course_credits = course_credits
        self.instructor = instructor
        self.org = org
        self.__create_id()

    def __create_id(self):
        self.id = _subject_id(self.org, self.year, self.group, self.subject_code, self.term)


def initialize_db():
    Base.metadata.create_all(bind=engine)
