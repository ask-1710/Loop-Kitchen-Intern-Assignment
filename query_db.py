import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List
import pytz
import pandas as pd


class StoreReport:
    def __init__(self, store_id):
        self.store_id = store_id
    
    def set_uptime_last_hour(self, active_minutes: int):
        self.uptime_last_hour = active_minutes

    def set_uptime_last_day(self, active_hours: int):
        self.uptime_last_day = active_hours

    def set_uptime_last_week(self, active_hours: int):
        self.uptime_last_week = active_hours

    def set_downtime_last_hour(self, inactive_minutes: int):
        self.downtime_last_hour = inactive_minutes
    
    def set_downtime_last_day(self, inactive_hours: int):
        self.downtime_last_day = inactive_hours

    def set_downtime_last_week(self, inactive_hours: int):
        self.downtime_last_week = inactive_hours
    
class TimingFunctions :
    def get_day_of_week(date: datetime)-> int:
        return date.weekday()

    def get_last_hour()->datetime:
        last_hour = datetime.today() - timedelta(hours = 1)
        return last_hour

    def get_last_week()->datetime:
        day = datetime.today()
        weekBefore = day - timedelta(days=7)
        return weekBefore

    def get_last_day()->datetime:
        today = datetime.today()
        last_day = today - timedelta(days = 1)
        return last_day

    def get_time_now()->datetime:
        return datetime.today()

    def construct_date(time_string: str, date: datetime)->datetime:        
        if date == None:
            date = datetime.today()

        date_string = date.strftime("%d/%m/%Y")
        datetime_string = date_string +" "+ time_string
        
        return datetime.strptime(datetime_string, '%d/%m/%Y %H:%M:%S')

    def get_next_week_day(week_day: int)->int:
        return (week_day+1)%7

class SQLiteOperations:

    def __init__(self, db_name:str):
        self.connection = None 
        self.cursor = None 
        self.connect(db_name)

    def connect(self, db_name:str)->None:
        self.connection = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def fetch_all_data_rows(self, table_name: str):
        if self.cursor == None:
            print("none")
        else:
            rows = self.cursor.execute("SELECT * FROM "+table_name)
            return rows.fetchall()

    def fetch_all_stores(self):
        all_rows = self.fetch_all_data_rows("LK_STORE_TIMEZONES")
        all_stores = [row[0] for row in all_rows] # return only store IDs
        return all_stores

    def fetch_store_timings_on_day(self, store_id: int, day_of_week: int):
        row = self.cursor.execute("SELECT * FROM LK_MENU_HOURS WHERE STORE_ID=? AND DAY=?",(store_id, day_of_week))
        return row.fetchone()[-2:]

    def fetch_store_activity(self, store_id: int, start_time: datetime, end_time: datetime):
        rows = self.cursor.execute("SELECT * FROM LK_STORE_STATUS WHERE STORE_ID=? AND TIMESTAMP_UTC BETWEEN ? AND ?",(store_id, start_time, end_time))
        return rows.fetchall()

    def fetch_store_timezone(self, store_id: int):
        rows = self.cursor.execute("SELECT timezone_str FROM LK_STORE_TIMEZONES WHERE STORE_ID=?",(store_id,))

        res = rows.fetchone()
        if(res == None or res == []) :
            return [store_id, 'America/Chicago']
        else:
            return res
        


def calculate_day_wise_activity(store_id: int, week_day: int, timezone_str: str, begin_range: None or datetime, end_range: None or datetime, last_hour: bool = False) -> List[int] :
    global sql_ops

    [start_time, end_time] = sql_ops.fetch_store_timings_on_day(store_id, week_day)
    
    start_date_obj = TimingFunctions.construct_date(start_time, begin_range)
    end_date_obj = TimingFunctions.construct_date(end_time, end_range)

    if(begin_range and start_date_obj < begin_range) : start_date_obj = begin_range
    if(end_range and end_date_obj > end_range) : end_date_obj = end_range
   

    local = pytz.timezone(timezone_str)
    local_dt = local.localize(start_date_obj, is_dst=None)
    utc_starttime = local_dt.astimezone(pytz.utc)
    
    local_dt = local.localize(end_date_obj, is_dst=None)
    utc_endtime = local_dt.astimezone(pytz.utc)

    activity = sql_ops.fetch_store_activity(store_id, utc_starttime, utc_endtime)
    active , inactive = 0 , 0
    num_readings = len(activity)
    if num_readings == 0 : return [0,0]
    if last_hour : duration = 60
    else : duration = 24
    duration /= num_readings
    for status in activity:
        
        if(status[2] == 'active'):
            active += 1
        else :
            inactive += 1
    
    active_duration = duration * active
    inactive_duration = duration * inactive

    return [active_duration, inactive_duration]


sql_ops = SQLiteOperations("loopkitchen.db")
result: Dict[str, StoreReport] = {}

def trigger_report(report_id: str)->None:
    global result
    store_ids = sql_ops.fetch_all_stores()

    rows: List[StoreReport] = []
    result[report_id] = rows
    print("STORE WISE REPORT")
    for store_id in store_ids:
        row = StoreReport(store_id=store_id)
        # CALCULATE FOR LAST HOUR
        last_hour = TimingFunctions.get_last_hour()
        last_hour_week_day = TimingFunctions.get_day_of_week(last_hour)
        curr_hour = TimingFunctions.get_time_now()
        timezone_str = sql_ops.fetch_store_timezone(store_id)[0]

        [active_minutes, inactive_minutes] = calculate_day_wise_activity(store_id, last_hour_week_day, timezone_str, last_hour, curr_hour, last_hour=True)
        row.set_uptime_last_hour(active_minutes)
        row.set_downtime_last_hour(inactive_minutes)

        # CALCULATE FOR LAST DAY
        begin_range = TimingFunctions.get_last_day()
        end_range = TimingFunctions.get_time_now()
        begin_week_day = TimingFunctions.get_day_of_week(begin_range)
        end_week_day = TimingFunctions.get_next_week_day(begin_week_day)
        [active_hours_day_1, inactive_hours_day_1] = calculate_day_wise_activity(store_id, begin_week_day, timezone_str, begin_range, None, False)
        [active_hours_day_2, inactive_hours_day_2] = calculate_day_wise_activity(store_id, end_week_day, timezone_str, None, end_range, False)

        total_active_hours = active_hours_day_1 + active_hours_day_2
        total_inactive_hours = inactive_hours_day_1 + inactive_hours_day_2

        row.set_uptime_last_day(total_active_hours)
        row.set_downtime_last_day(total_inactive_hours)

        # CALCULATE FOR LAST WEEK
        begin_range = TimingFunctions.get_last_week()
        end_range = TimingFunctions.get_time_now()

        begin_week_day = TimingFunctions.get_day_of_week(begin_range)
        [active_hours, inactive_hours] = calculate_day_wise_activity(store_id, begin_week_day, timezone_str, begin_range, None, False)
        total_active_hours = active_hours
        total_inactive_hours = inactive_hours

        next_week_day = TimingFunctions.get_next_week_day(begin_week_day)

        while next_week_day != begin_week_day-1:
            [active_duration, inactive_duration] = calculate_day_wise_activity(store_id, next_week_day, timezone_str, None, None, False)
            total_inactive_hours += inactive_duration
            total_active_hours += active_duration
            next_week_day = TimingFunctions.get_next_week_day(next_week_day)

        [active_duration, inactive_duration] = calculate_day_wise_activity(store_id, next_week_day, timezone_str, None, end_range, False)
        total_active_hours += active_duration
        total_inactive_hours += inactive_duration

        row.set_uptime_last_week(total_active_hours)
        row.set_downtime_last_week(total_inactive_hours)

        rows.append(row)

    result[report_id] = rows


def get_final_report_status(report_id: str)->bool:
    global result
    if report_id not in result:
        raise Exception("invalid report id")

    return len(result[report_id])>0


def deserialize_report(report_id: int) -> pd.DataFrame :
    global result
    data = {}

    data['store_id'] = [report.store_id for report in result[report_id]]
    data['uptime_last_hour(in minutes)'] = [report.uptime_last_hour for report in result[report_id]]
    data['uptime_last_day(in hours)'] = [report.uptime_last_day for report in result[report_id]]
    data['uptime_last_week(in hours)'] = [report.uptime_last_week for report in result[report_id]]
    data['downtime_last_hour(in minutes)'] = [report.downtime_last_hour for report in result[report_id]]
    data['downtime_last_day(in hours)'] = [report.downtime_last_day for report in result[report_id]]
    data['downtime_last_week(in hours)'] = [report.downtime_last_week for report in result[report_id]]

    df = pd.DataFrame(data)
    return df    