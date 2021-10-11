from quart import current_app, session
from app.timetable import Timetable, weekdays


def _get_session_timetable() -> Timetable:
    try:
        session['timetable']
    except KeyError:
        session['timetable'] = Timetable().to_json()
    tt = Timetable()
    tt.load_json(session['timetable'])
    return tt


def _update_session_timetable(tt: Timetable):
    print(tt.__dict__)
    session.update({'timetable': tt.to_json()})


def get_weekdays() -> list:
    return weekdays


def current_timetable() -> dict:
    return {'success': True, 'timetable': _get_session_timetable().dump()}


def build_timetable(subject_code: list) -> dict:
    success = False
    tt = _get_session_timetable()
    subjects = current_app.syllabus.get_from_bulk_id(subject_code)
    for s in subjects:
        result = tt.add(s)
        if not result:
            break
    else:
        success = True
        _update_session_timetable(tt)
    return {'success': success, 'timetable': tt.dump()}


def empty_timetable() -> dict:
    tt = _get_session_timetable()
    tt.empty()
    _update_session_timetable(tt)
    return {'success': True, 'timetable': tt.dump()}


def get_available():
    tt = _get_session_timetable()
    return current_app.syllabus.get_available('2021', 'trans', tt.to_json())


def get_all():
    return current_app.syllabus.get_all('2021', 'trans')
