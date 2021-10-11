from quart import render_template, request
from app import quart_app, api


@quart_app.route('/')
async def index():
    return await render_template(
        'index.html',
        title='Index'
    )


@quart_app.route('/api')
async def api_index():
    return await render_template(
        'index.html',
        title='API Documents'
    )


@quart_app.route('/timetable')
async def get_timetable():
    req_values = await request.values
    if req_values.getlist("subject"):
        result = api.build_timetable(req_values.getlist("subject"))
        subjects_available = api.get_available()
    else:
        result = api.empty_timetable()
        subjects_available = api.get_all()
    return await render_template(
        'timetable.html',
        title='Timetable',
        weekdays=api.weekdays,
        current_timetable=result['timetable'],
        subjects_available=subjects_available
    )