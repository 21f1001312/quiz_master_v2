from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from zoneinfo import ZoneInfo
from applications.models import db, Quiz, QuizAttempt, User
from jinja2 import Template
from applications.quiz_worker import celery
from celery.schedules import crontab
import smtplib
import os
import csv

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ─── Email Utilities ──────────────────────────────────────────────────────────

def send_mail(email, subject, email_content, attachment=None):
    smtp_server_host = 'localhost'
    smtp_port = 1025
    sender_email = 'admin@gmail.com'
    sender_password = 'admin123'

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(email_content, 'html'))

    if attachment:
        with open(attachment, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename={os.path.basename(attachment)}")
            msg.attach(part)

    server = smtplib.SMTP(host=smtp_server_host, port=smtp_port)
    try:
        server.login(sender_email, sender_password)
    except smtplib.SMTPException:
        print("SMTP login skipped (likely using MailHog)")
    server.send_message(msg)
    server.quit()
    print(f"Mail sent to {email}")


# ─── HTML Template Helper ─────────────────────────────────────────────────────

def get_html_report_template(username, data):
    template_path = os.path.join(os.path.dirname(__file__), 'report.html')
    with open(template_path, "r") as file:
        template = Template(file.read())
    return template.render(username=username, data=data)


# ─── Celery Periodic Tasks ────────────────────────────────────────────────────

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, test.s('hello'), name='debug test')
    sender.add_periodic_task(60.0, daily_reminder.s(), name='daily quiz reminder')
    sender.add_periodic_task(
        crontab(day_of_month='1', hour=7, minute=0),
        monthly_report.s(),
        name='monthly performance report'
    )


@celery.task
def test(arg):
    print(f"[Test Task] {arg}")


@celery.task
def daily_reminder():
    students = User.query.filter_by(role='student').all()
    for student in students:
        msg = f"<h3>Hello {student.full_name}, don't forget to check your scheduled quizzes today!</h3>"
        send_mail(email=student.username, subject="Daily Quiz Reminder", email_content=msg)
    print("Daily reminders sent.")


@celery.task
def monthly_report():
    students = User.query.filter_by(role='student').all()
    for student in students:
        attempts = QuizAttempt.query.filter_by(student_id=student.id).all()
        summary = []

        for attempt in attempts:
            quiz = Quiz.query.get(attempt.quiz_id)
            if quiz:
                summary.append([
                    quiz.title,
                    quiz.date_of_quiz.strftime('%Y-%m-%d'),
                    attempt.total_scored or 0,
                    'Submitted' if attempt.submitted else 'Not Submitted'
                ])

        html = get_html_report_template(student.full_name, summary)
        send_mail(email=student.username, subject="Monthly Quiz Performance", email_content=html)
    print("Monthly reports sent.")


@celery.task
def data_export(data: list[dict], email: str):
    export_dir = os.path.join(os.path.dirname(__file__), 'exports')
    os.makedirs(export_dir, exist_ok=True)

    csv_path = os.path.join(export_dir, 'data_export.csv')
    fieldnames = list(data[0].keys()) if data else []

    with open(csv_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    send_mail(
        email=email,
        subject="Quiz History Export",
        email_content="Please find your exported quiz history.",
        attachment=csv_path
    )
    print("Data export completed.")
    return "Export successful"

@celery.task
def schedule_quiz_submission(attempt_id):
    # Logic to automatically submit the quiz attempt
    attempt = QuizAttempt.query.get(attempt_id)
    if attempt:
        attempt.submitted = True
        db.session.commit()
        print(f"Quiz attempt {attempt_id} submitted automatically.")
    else:
        print(f"Quiz attempt {attempt_id} not found.")

from flask import send_file
import io

class QuizExportDownloadAPI(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        attempts = QuizAttempt.query.filter_by(student_id=user_id).all()

        data = []
        for a in attempts:
            quiz = Quiz.query.get(a.quiz_id)
            if quiz:
                data.append({
                    "Quiz Title": quiz.title,
                    "Date": quiz.date_of_quiz.strftime('%Y-%m-%d'),
                    "Score": a.total_scored or 0,
                    "Status": "Submitted" if a.submitted else "Not Submitted"
                })

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

        output.seek(0)
        return send_file(
            io.BytesIO(output.read().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name='quiz_history.csv'
        )
    
    @celery.task
    def data_export(data: list[dict], email: str):
        export_dir = os.path.join(os.path.dirname(__file__), 'exports')
        os.makedirs(export_dir, exist_ok=True)

        csv_path = os.path.join(export_dir, 'data_export.csv')
        fieldnames = list(data[0].keys()) if data else []

        with open(csv_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        send_mail(
            email=email,
            subject="Quiz History Export",
            email_content="Please find your exported quiz history.",
            attachment=csv_path
        )
        print(f"[Celery] Export complete and mailed to {email}")
        return "Export successful"
    
    
