from common.utils import TypeWeek
from timetable.celery import app
from university.models import UniversityInfo


@app.task()
def change_current_type_of_week():
    """
    Every week type_of_week is changed to opposite.
    """
    infos = UniversityInfo.objects.all()
    for university_info in infos:
        current_type_of_week = university_info.data.get('current_type_of_week')
        if current_type_of_week in TypeWeek.data():
            reversed_type_of_week = TypeWeek.get_reversed(current_type_of_week)
            university_info.data.update({'current_type_of_week': reversed_type_of_week})
            university_info.save()
