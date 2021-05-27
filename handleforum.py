from datetime import datetime
import json

import config as db


def loadfile(sessionid):
    fname = '/static/api/' + sessionid + '.json'
    file = open(fname, "r")
    cl = file.read()
    return json.loads(cl)


def store(sid):
    course_db = db.conn.cursor()

    sql = "INSERT IGNORE INTO courses (course_id, academic_year, semester, course_dpm_id, course_dpm_abbr," \
          "course_name, course_name_en, semester_index, course_group, is_required, is_required_en, course_units) " \
          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s); "

    result = loadfile(sid)

    for i in range(0, len(result['grades'])):
        course_id = result['grades'][i]['course_id'] + result['grades'][i]['academic_year'] + '0' + result['grades'][i]['semester']

        val = (course_id,
               result['grades'][i]['academic_year'],
               result['grades'][i]['semester'],
               result['grades'][i]['course_dpm_id'],
               result['grades'][i]['course_dpm_abbr'],
               result['grades'][i]['course_name'],
               result['grades'][i]['course_name_en'],
               result['grades'][i]['semester_index'],
               result['grades'][i]['course_group'],
               result['grades'][i]['is_required'],
               result['grades'][i]['is_required_en'],
               result['grades'][i]['course_units'])

        course_db.execute(sql, val)
        db.conn.commit()


def querySearch(year, term, dpm):
    course_db = db.conn.cursor()

    if year == 'all' and term == 'all' and dpm == 'all':
        sql = "SELECT * FROM courses " \
              "ORDER BY academic_year DESC ;"
    elif year != 'all' and term == 'all' and dpm == 'all':
        sql = "SELECT * FROM courses WHERE academic_year = '" + year + "' " \
              "ORDER BY academic_year DESC ;"
    elif year == 'all' and term != 'all' and dpm == 'all':
        sql = "SELECT * FROM courses WHERE semester = '" + term + "' " \
              "ORDER BY academic_year DESC ;"
    elif year == 'all' and term == 'all' and dpm != 'all':
        sql = "SELECT * FROM courses WHERE course_dpm_id LIKE '" + dpm + "%' " \
              "ORDER BY academic_year DESC ;"
    elif year == 'all' and term != 'all' and dpm != 'all':
        sql = "SELECT * FROM courses " \
              "WHERE semester = '" + term + "' AND course_dpm_id LIKE '" + dpm + "%' " \
              "ORDER BY academic_year DESC ;"
    elif year != 'all' and term == 'all' and dpm != 'all':
        sql = "SELECT * FROM courses " \
              "WHERE academic_year = '" + year + "' AND course_dpm_id LIKE '" + dpm + "%' " \
              "ORDER BY academic_year DESC ;"
    elif year != 'all' and term != 'all' and dpm == 'all':
        sql = "SELECT * FROM courses " \
              "WHERE academic_year = '" + year + "' AND semester = '" + term + "' " \
              "ORDER BY academic_year DESC ;"
    elif year != 'all' and term != 'all' and dpm != 'all' and year is not None and term is not None and dpm is not None:
        sql = "SELECT * FROM courses " \
              "WHERE academic_year = '" + year + "' AND semester = '" + term + "' AND course_dpm_id = '" + dpm + "' " \
              "ORDER BY academic_year DESC ;"
    else:
        sql = "SELECT * FROM courses " \
              "WHERE academic_year = '109' " \
              "ORDER BY academic_year DESC ;"

    course_db.execute(sql)
    result = course_db.fetchall()

    return result


def getAcademicYear():
    course_db = db.conn.cursor()

    sql = "SELECT academic_year FROM courses ORDER BY academic_year ASC ;"
    course_db.execute(sql)
    result = course_db.fetchall()

    return [result[0][0], result[len(result)-1][0]]


def searchCourse(course_id):
    course_db = db.conn.cursor()

    sql = 'SELECT * FROM courses WHERE course_id = "' + course_id + '";'
    course_db.execute(sql)
    result = course_db.fetchone()

    return result


def writeComment(sessionid, comment, courseid):
    course_db = db.conn.cursor()

    sql = "INSERT INTO comments (course_id, student_id, content, establish)" \
          "VALUES (%s, %s, %s, %s); "
    comment_plusone_sql = 'UPDATE courses SET comment = comment + 1 WHERE course_id = "' + courseid + '\";'

    val = (
        courseid,
        sessionid,
        comment,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

    course_db.execute(sql, val)
    db.conn.commit()
    course_db.execute(comment_plusone_sql)
    db.conn.commit()


def fetchCommentByCourseid(courseid):
    course_db = db.conn.cursor()
    sql = 'SELECT * FROM comments WHERE course_id LIKE "' + courseid + '" ORDER BY establish DESC;'
    course_db.execute(sql)
    result = course_db.fetchall()

    comments = []
    for c in result:
        comment = {
            'course_id':    c[1],
            'student_id':   c[2],
            'message':      c[3],
            'establish':    c[4]
        }
        comments.append(comment)

    return comments
