from shutil import copyfile
from random import randrange

from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from datetime import timedelta

from calallcredits import *
from handleforum import *
from extensions import *
from tkucrawler import *

import requests

app = Flask(__name__)

exp_days = 3

app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=exp_days)


# --- 首頁 -----------------------------------------------------
@app.route('/')
def index():
    session['goalurl'] = 'index'
    return render_template('index.html', title="首頁｜TKU")


# --- 登入 -----------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('is_login') == 1:
        return redirect(url_for('index'))
    elif request.method == 'POST':
        user_id = decode_base64(request.form['username'])
        user_pw = decode_base64(request.form['password'])

        autoGetGradeAndStdInfo(user_id, user_pw)
        session['is_login'] = 1
        session['username'] = user_id

        # --- 如果有目標連結，則直接導向該網址
        if session.get('goalurl') != "" or session.get('goalurl') is not None:
            return redirect(url_for(session.get('goalurl')))
        else:
            return redirect(url_for(session['index']))
    else:
        return render_template('login.html', title="登入｜TKU")


# --- 登出 -----------------------------------------------------
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    try:
        fname = api_path + session.get('username') + '.json'
        os.remove(fname)
        session['is_login'] = 0
        session['username'] = ""
    except OSError as e:
        print(e)

    return redirect(url_for('index'))


# --- 畢業學分 -----------------------------------------------------
@app.route('/requirements')
def requirements():
    session['goalurl'] = 'requirements'
    if session.get('is_login'):
        avatar = ['lion', 'mouse', 'dog', 'monkey', 'fox', 'pig', 'rabbit', 'panda', 'owl', 'cat']
        i = int(session.get('username')[-1])

        liberalcourse = convertStrToJson(session.get('username'))
        clublearningcourse = clublearning(session.get('username'))
        requirementslist = accumulated_required_elective(session.get('username'))
        basiccourselist = cal_basic_course(session.get('username'))
        liberallist = cal_liberal_group(session.get('username'))

        return render_template('requirements.html', title="畢業學分｜TKU", liberal=liberalcourse, avatar=avatar[i], requirements_list=requirementslist, basic_course=basiccourselist, clublearning=clublearningcourse, liberallist=liberallist)
    else:
        return redirect(url_for('login'))


# --- 歷史成績 -----------------------------------------------------
@app.route('/history', methods=['GET', 'POST'])
def history_grade():
    session['goalurl'] = 'history_grade'
    if session.get('is_login'):
        g = convertStrToJson(session.get('username'))
        return render_template('history.html', title="歷史成績｜TKU", grades=g)
    else:
        return redirect(url_for('login'))


# --- 課程評論 -----------------------------------------------------
@app.route('/forum', methods=['GET', 'POST'])
def forum():
    session['goalurl'] = 'forum'
    if session.get('is_login'):
        if request.method == 'GET':
            year = request.values.get('academic_year')
            semester = request.values.get('semester')
            dpm = request.values.get('dpm')

            if year is not None and semester is not None and dpm is not None:
                course_list = querySearch(year, semester, dpm)
            else:
                course_list = querySearch(None, None, None)

            message = ""
            if len(course_list) == 0:
                message = "依照查詢條件，目前並無選課紀錄"

            allYears = getAcademicYear()
            return render_template('forum.html', title="課程評價｜TKU", courses=course_list, years=allYears, msg=message, y=year)
    else:
        return redirect(url_for('login'))


@app.route('/forum/<string:artical_id>', methods=['GET', 'POST'])
def forum_artical(artical_id):
    session['goalurl'] = 'forum'
    if session.get('is_login'):
        formal_id = ""
        # --- 切割字串回正常id
        for i in range(0, math.floor(len(artical_id)), 2):
            formal_id += chr(int(artical_id[i:i+2]))

        result = searchCourse(formal_id)
        course = {
            "course_id":        result[0],      # --- e.g. A045710901
            "course_dpm_id":    result[3],      # --- e.g. TNUMB
            "course_dpm_abbr":  result[4],      # --- e.g. 藝術欣賞學門
            "course_no":        result[0][:5],  # --- e.g. A0457
            "course_name":      result[5],      # --- e.g. 表演藝術
            "course_name_en":   result[6],      # --- e.g. PERFORMANCE ARTS
            "is_required":      result[9]       # --- e.g. 必修
        }

        if request.method == 'POST':
            writeComment(session.get('username'), request.form['comment'], formal_id)

        comments = []
        result = fetchCommentByCourseid(formal_id)
        for c in result:
            avatar = ['lion', 'mouse', 'dog', 'monkey', 'fox', 'pig', 'rabbit', 'panda', 'owl', 'cat']
            c['icon_img'] = avatar[int(c['student_id'][-1])]
            comments.append(c)

        return render_template('artical.html', title=course['course_name']+"｜TKU", course=course, comments=comments)
    else:
        return redirect(url_for('login'))


# --- 聯絡我們 -----------------------------------------------------
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        msg = request.form['msg']
        sendRecommendEmail(name, email, msg)
        return render_template('contact.html', title="聯絡我們｜TKU", sendComplete="true")
    else:
        return render_template('contact.html', title="聯絡我們｜TKU")


# --- 成績api -----------------------------------------------------
@app.route('/api/grades/<int:student_id>', methods=['GET'])
def grades(student_id):
    if str(student_id) == session.get('username'):
        fname = 'static/api/' + str(student_id) + '.json'
        file = open(fname, "r")
        return json.loads(file.read())
    else:
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
