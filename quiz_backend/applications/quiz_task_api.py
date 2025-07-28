import os
import smtplib
import csv
import io
from datetime import datetime, time
from celery.schedules import crontab
from flask import send_file
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from applications.models import db, Quiz, QuizAttempt, User, Question, QuizAttemptAnswer
from applications.quiz_worker import celery
from jinja2 import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pytz  

IST = pytz.timezone('Asia/Kolkata') 

# ─── Email Utility ──────────────────────────────────────

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
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(attachment)}")
            
            msg.attach(part)

    server = smtplib.SMTP(host=smtp_server_host, port=smtp_port)

    try:
        server.login(sender_email, sender_password)
    except smtplib.SMTPException:
        print("SMTP login skipped (likely using MailHog)")

    server.send_message(msg)
    server.quit()
    print(f"Mail sent to {email}")

# ─── HTML Report Template Helper ────────────────────────

def get_html_report_template(username, data, avg_score=None, total_quizzes=None):
    current_dir = os.path.abspath(os.path.dirname(__file__))
    report_path = os.path.join(current_dir, '..', 'report.html')
    report_path = os.path.abspath(report_path) 
    with open(report_path, "r") as file:
        jinja_template = Template(file.read())
    return jinja_template.render(
        username=username,
        data=data,
        avg_score=avg_score,
        total_quizzes=total_quizzes
    )

# ─── Celery Periodic Tasks Setup ────────────────────────

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, test_task.s('hello'), name='test every 10s')

    sender.add_periodic_task(
        crontab(hour=16, minute=5), 
        daily_reminder.s(),
        name='daily quiz reminder'
    )

    sender.add_periodic_task(
        crontab(day_of_month='28'),
        monthly_report.s(),
        name='monthly performance report'
    )

# ─── Celery Tasks ───────────────────────────────────────

@celery.task
def test_task(arg):
    print(f"running test task with arg: {arg}")

@celery.task
def daily_reminder():
    students = User.query.filter_by(role='student', status='active').all()
    for student in students:
        msg = f"<h3>Hello {student.full_name}, don't forget to check your scheduled quizzes today!</h3>"
        send_mail(
            email=student.username,
            subject="Daily Quiz Reminder",
            email_content=msg
        )
    print("Daily reminders sent.")

@celery.task
def monthly_report():
    students = User.query.filter_by(role='student', status='active').all()
    for student in students:
        attempts = QuizAttempt.query.filter_by(student_id=student.id).all()
        summary = []
        total_quizzes = len(attempts)
        total_score = sum(a.total_scored or 0 for a in attempts)
        avg_score = (total_score / total_quizzes) if total_quizzes else 0
        for attempt in attempts:
            quiz = Quiz.query.get(attempt.quiz_id)
            if quiz:
                quiz_date = quiz.date_of_quiz.strftime('%Y-%m-%d')
                summary.append([
                    quiz.title,
                    quiz_date,
                    attempt.total_scored or 0,
                    'Submitted' if attempt.submitted else 'Not Submitted'
                ])
        html_report = get_html_report_template(
            username=student.full_name,
            data=summary,
            avg_score=avg_score,
            total_quizzes=total_quizzes
        )
        send_mail(
            email=student.username,
            subject="Monthly Report",
            email_content=html_report
        )
    print("Monthly reports sent.")


@celery.task
def schedule_quiz_submission(attempt_id):
    attempt = QuizAttempt.query.get(attempt_id)
    
    if not attempt:
        print(f"Attempt ID {attempt_id} not found.")
        return

    if attempt.submitted:
        print(f"Attempt ID {attempt_id} already submitted.")
        return

    quiz = Quiz.query.get(attempt.quiz_id)
    if not quiz:
        print(f"Quiz ID {attempt.quiz_id} not found.")
        return

    questions = Question.query.filter_by(quiz_id=quiz.id).all()

    # Auto-fill unanswered questions with blank submissions
    for question in questions:
        existing_answer = QuizAttemptAnswer.query.filter_by(
            attempt_id=attempt.id,
            question_id=question.id
        ).first()
        if not existing_answer:
            blank_answer = QuizAttemptAnswer(
                attempt_id=attempt.id,
                question_id=question.id,
                selected_option=None,
                is_correct=False,
                quiz_id=quiz.id
            )
            db.session.add(blank_answer)

    # Mark attempt as submitted with 0 score if nothing correct
    if attempt.total_scored is None:
        attempt.total_scored = 0

    attempt.submitted = True
    db.session.commit()
    print(f"Quiz attempt {attempt_id} auto-submitted.")


# ─── CSV Download API Resource ──────────────────────────

@celery.task
def data_export(data, email):
    csv_path = os.path.join(os.path.dirname(__file__), 'data_export.csv')
    
    # Handle empty list
    if not data:
        print("No data to export.")
        return "No data"

    # Dynamically extract headers
    fieldnames = list(data[0].keys())

    with open(csv_path, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    send_mail(
        email=email,
        email_content="Attached is your quiz attempt report.",
        subject="Quiz Attempt Export",
        attachment=csv_path
    )

    print("Data exported and emailed successfully.")
    return "Export Done"

