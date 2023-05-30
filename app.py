from flask import Flask, render_template, request, redirect, url_for
from flask import send_file
import time
import atexit
from datetime import datetime

app = Flask(__name__, template_folder="templates")


reportID = ''
@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/generate_report/', methods=['GET','POST'])
def generate_report():
    return "Report is being generated!"

@app.route('/check_report_status/', methods=['GET','POST'])
def check_report_status(reportID):
    return "Report is being processed..."


if __name__ == '__main__':

    app.run(host='0.0.0.0', debug=True)




'''
OPTIMIZATION of CODE:


# from apscheduler.schedulers.background import BackgroundScheduler

def pre_calculation_activity_hours():
    UTCtime = datetime.utcnow()
    print('Recording status' + str(UTCtime))
    

# CODE TO ADD SCHEDULER

scheduler = BackgroundScheduler()
scheduler.add_job(func=here_goes_record_status, trigger="interval", seconds=10)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())
'''
