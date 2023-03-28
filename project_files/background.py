from project_files import scheduler
from project_files import SESSIONS, EVENTS, DATA

from .scripts.functions import delete_expired_data


scheduler.add_job(delete_expired_data, args=[0, 0, 20, SESSIONS], trigger='interval', minutes=15)
scheduler.add_job(delete_expired_data, args=[7, 0, 0, EVENTS], trigger='interval', days=1)
scheduler.add_job(delete_expired_data, args=[7, 0, 0, DATA], trigger='interval', days=1)

scheduler.start()