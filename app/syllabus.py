"""

"""
import requests
import sqlalchemy.exc
from sqlalchemy import tuple_, or_

from app import quart_app, db
from app.db import SyllabusSubjects
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta


class Jaist:
    def __init__(self):
        self.org = 'jaist'
        self.index_url = quart_app.config['JAIST_SYLLABUS'] + "index.php"
        self.list_url = quart_app.config['JAIST_SYLLABUS'] + "List_Syllabus.php"
        self.detail_url = quart_app.config['JAIST_SYLLABUS'] + "View_Syllabus.php"
        self.current_year = datetime.now(tz=timezone(timedelta(hours=+9), 'JST')).year
        self.csrf = ''
        self.php_session_id = ''
        self.__check_cache()

    def __check_cache(self):
        result = db.session.query(db.SyllabusSubjects).all()
        if not result:
            self.__set_jaist_credentials()
            subjects = self.__fetch_subject_list()
            self.__update_subject_cache(subjects)

    def __set_jaist_credentials(self):
        raw = requests.get(self.index_url, verify=False)
        soup = BeautifulSoup(raw.content, 'html.parser')
        try:
            self.csrf = soup.find('input', {'name': 'security_post_value'}).get('value')
            self.php_session_id = raw.cookies['PHPSESSID']
        except Exception as e:
            print(e)

    def __update_subject_cache(self, subjects: [SyllabusSubjects]):
        for subject in subjects:
            try:
                with db.session.begin():
                    db.session.add(subject)
            except sqlalchemy.exc.IntegrityError:
                continue

    def __fetch_subject_list(self) -> [SyllabusSubjects]:
        subjects = []
        page_number = 1
        try:
            raw = self.__request_subject_list_page(page_number)
            soup = BeautifulSoup(raw.content, 'html.parser')
            max_page = int(soup.findAll('table')[-1].findAll('a')[-1].string)
            subjects.extend(self.__extract_subjects_from_soup(soup))
            if max_page > page_number:
                for i in range(1, max_page):
                    page_number += 1
                    raw = self.__request_subject_list_page(page_number)
                    soup = BeautifulSoup(raw.content, 'html.parser')
                    subjects.extend(self.__extract_subjects_from_soup(soup))
        except ConnectionError as e:
            print(e)
        except ValueError as e:
            print(e)
        return subjects

    def __request_subject_list_page(self, page_number) -> requests.Response:
        payload = {
            "sel_web_year": self.current_year,
            "security_post_value": self.csrf,
            "hid_pagemode": "first",
            "hid_mysyllabus_list": "",
            "hid_MySy_back": "index",
            "hid_nowpage": page_number
        }
        raw = requests.post(self.list_url, data=payload, verify=False,
                            headers={'Content-Type': 'application/x-www-form-urlencoded'},
                            cookies={'PHPSESSID': self.php_session_id}
                            )
        if len(raw.content) < 25000:
            raise ValueError
        return raw

    def __extract_subjects_from_soup(self, soup) -> [SyllabusSubjects]:
        subjects = []
        rows = soup.find('table', class_='ListTbl_web').findAll('tr')
        keys = []
        for row in rows:
            if not keys:
                cols = row.find_all('th')
                for col in cols:
                    text = col.string if col.string else col.find('span', class_='Language_En').text
                    if text:
                        keys.append(text)
            cols = row.find_all('td')
            if cols:
                elements = []
                elements_ja = []
                for col in cols:
                    text = col.string if col.string else col.find('span', class_='Language_En')\
                        .get_text(separator="_").strip()
                    if text or len(elements) > 3:
                        elements.append(text)
                        elements_ja.append(col.string if col.string else col.find('span', class_='Language_Jp')
                                           .text.split('\u3000', 1)[0].rstrip())
                if len(elements) == len(keys):
                    term = elements[keys.index('Term')].replace('Term ', '')
                    period = elements[keys.index('Day & Period')].replace('／', '/')
                    title_ja = elements_ja[keys.index('Course Title')]
                    if '_' in elements[keys.index('Term')]:
                        terms = term.split('_')
                        periods = period.split('_')
                        if len(periods) == 1:
                            periods.append('')
                        for i, term in enumerate(terms):
                            subject = SyllabusSubjects(
                                year=self.current_year,
                                group=elements[keys.index('Course Number')][0],
                                subject_code=elements[keys.index('Course Number')],
                                title=elements[keys.index('Course Title')],
                                title_ja=title_ja,
                                term=term,
                                period=periods[i],
                                course_credits=elements[keys.index('Credits')],
                                instructor=elements[keys.index('Instructor')],
                                org=self.org
                            )
                            subjects.append(subject)
                    else:
                        subject = SyllabusSubjects(
                            year=self.current_year,
                            group=elements[keys.index('Course Number')][0],
                            subject_code=elements[keys.index('Course Number')],
                            title=elements[keys.index('Course Title')],
                            title_ja=title_ja,
                            term=term,
                            period=period,
                            course_credits=elements[keys.index('Credits')],
                            instructor=elements[keys.index('Instructor')],
                            org=self.org
                        )
                        subjects.append(subject)
            else:
                continue
        return subjects

    def get(self, year, subject_code):
        pass

    def _fetch(self, subject_code):
        pass


class Kanazawa:
    def __init__(self):
        pass


class Syllabus:
    def __init__(self):
        self.jaist = Jaist()
        self.kanazawa = Kanazawa()

    def get_all(self, year, department):
        if department == 'trans':
            result = db.session.query(db.SyllabusSubjects).filter_by(year=year)\
                .filter(~db.SyllabusSubjects.term.like('Tokyo')).all()
        elif department == 'tokyo':
            result = db.session.query(db.SyllabusSubjects).filter_by(year=year, org='jaist').all()
        else:
            result = db.session.query(db.SyllabusSubjects).filter_by(year=year, org='jaist') \
                .filter(~db.SyllabusSubjects.term.like('Tokyo')).all()
        return result

    def get_available(self, year, department, current_timetable: dict):
        occupied = [p.split('_') for p in current_timetable['period_occupied']]
        if department == 'trans':
            result = db.session.query(db.SyllabusSubjects).filter_by(year=year) \
                .filter(~db.SyllabusSubjects.term.like('Tokyo%')) \
                .filter(~db.SyllabusSubjects.id.in_(current_timetable['subject_id'])).all()
        elif department == 'tokyo':
            result = db.session.query(db.SyllabusSubjects).filter_by(year=year, org='jaist') \
                .filter(~db.SyllabusSubjects.term.like('%-%')) \
                .filter(~db.SyllabusSubjects.id.in_(current_timetable['subject_id'])).all()
        else:
            result = db.session.query(db.SyllabusSubjects).filter_by(year=year, org='jaist') \
                .filter(~db.SyllabusSubjects.term.like('Tokyo%')) \
                .filter(~db.SyllabusSubjects.id.in_(current_timetable['subject_id'])).all()
        for o in occupied:
            excluded = []
            for r in result:
                if r.term == o[0] and o[1] in r.period:
                    continue
                else:
                    excluded.append(r)
            else:
                result = excluded
        return result

    def get(self, year, subject_code):
        pass

    def get_from_id(self, syllabus_id):
        pass

    def get_from_bulk_id(self, syllabus_id: list):
        result = db.session.query(db.SyllabusSubjects).filter(db.SyllabusSubjects.id.in_(syllabus_id)).all()
        return result
