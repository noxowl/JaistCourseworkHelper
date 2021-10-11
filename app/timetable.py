"""

"""
import calendar

from app.db import SyllabusSubjects

weekdays = [day[:3] for day in calendar.day_name[:5]]
term = ['1-1', '1-2', '2-1', '2-2']
period = [1, 2, 3, 4, 5]


def set_empty_timetable() -> dict:
    timetable = {}
    for t in term:
        timetable[t] = {}
        for i, day in enumerate(weekdays):
            # timetable[t].update({'{0}'.format(i): ['{0}{1}{2}'.format(t, day, p) for p in period]})
            timetable[t].update({'{0}'.format(i): ['' for p in period]})
    return timetable


_empty_timetable = set_empty_timetable()


class Timetable:
    def __init__(self):
        self.timetable = _empty_timetable
        self.subject_id = []
        self.period_occupied = []

    def empty(self):
        self.timetable = _empty_timetable
        self.subject_id = []

    def add(self, subject: SyllabusSubjects) -> bool:
        success = False
        periods = subject.period.split('/')
        for p in periods:
            if p:
                if not self.timetable[subject.term][str(weekdays.index(p[:-1]))][int(p[-1]) - 1]:
                    self.timetable[subject.term][str(weekdays.index(p[:-1]))][int(p[-1]) - 1] = subject.subject_code
                    success = True
                else:
                    success = False
        if success:
            for p in periods:
                self.period_occupied.append('{0}_{1}'.format(subject.term, p))
            self.subject_id.append(subject.id)
        return success

    def available(self):
        pass

    def dump(self):
        dump_table = {}
        for k, v in self.timetable.items():
            dump_table.update({k: []})
            for period_index, p in enumerate(period):
                try:
                    dump_table[k][period_index]
                except IndexError:
                    dump_table[k].append([])
                for day, subs in v.items():
                    dump_table[k][period_index].append(subs[period_index])
        return dump_table

    def load_json(self, json):
        try:
            self.timetable = json['timetable']
            self.subject_id = json['subject_id']
            self.period_occupied = json['period_occupied']
        except KeyError:
            self.empty()

    def to_json(self):
        return {'timetable': self.timetable, 'subject_id': self.subject_id, 'period_occupied': self.period_occupied}


