import json
import math


def loadfile(sessionid):
    fname = 'static/api/' + sessionid + '.json'
    file = open(fname, "r")
    cl = file.read()
    return json.loads(cl)


def clublearning(sessionid):
    result = loadfile(sessionid)

    basic_course = "無成績"
    event_engage = "未完成"
    event_launch = "未完成"

    for grade in result['grades']:
        if "入門課程" in grade['course_name']:
            basic_course = grade['grade']
        if "活動參與" in grade['course_name']:
            event_engage = grade['grade']
        if "活動執行" in grade['course_name']:
            event_launch = grade['grade']

    clublearningcourse = {
        'basic_course': basic_course,
        'event_engage': event_engage,
        'event_launch': event_launch
    }

    return clublearningcourse


def accumulated_required_elective(sessionid):
    result = loadfile(sessionid)

    liberal_list = ['L', 'P', 'V', 'M', 'T', 'R', 'W', 'S', 'O', 'Z', 'U']

    total_graduation_credit = result['requirement']['grad_credit']
    total_required_credit = result['requirement']['required']  # --- 本系必修(基本課程、通識、系定)
    total_elective_credit = result['requirement']['elective']  # --- 本系最低選修(未加自由選修)

    total_credits = 0  # --- 所有選修(包含系上選修跟自由選修)

    accumulated_required = 0  # --- 累積所有必修學分
    accumulated_elective = 0  # --- 累積系上選修學分

    liberal_credit = 0
    basic_course = 0

    for r in result['grades']:
        # --- 所有學分
        if str(r['grade']).isdigit() and "入門課程" not in r['course_name']:
            if r['grade'] >= 60:
                total_credits += r['course_units']
        elif "入門課程" in r['course_name'] and int(r['grade']) >= 60:
            total_credits += 1/3
        elif "活動參與" in r['course_name'] and "通過" in r['grade']:
            total_credits += 1/3
        elif "活動執行" in r['course_name'] and "通過" in r['grade']:
            total_credits += 1/3
        elif r['grade'] == "通過":
            total_credits += r['course_units']

        # --- 所有必修學分總和
        if "必修" in r['is_required']:
            if "進修英文" in r['course_name']:
                if r['grade'] >= 60:
                    accumulated_elective += r['course_units']
            elif str(r['grade']).isdigit():
                if int(r['grade']) >= 60:
                    accumulated_required += r['course_units']
            elif "通過" in r['grade']:
                accumulated_required += r['course_units']
            if "入門課程" in r['course_name'] and int(r['grade']) >= 60:
                accumulated_required += 1 / 3
            elif "活動參與" in r['course_name'] and "通過" in r['grade']:
                accumulated_required += 1 / 3
            elif "活動執行" in r['course_name'] and "通過" in r['grade']:
                accumulated_required += 1 / 3

        # --- 選修學分總和 ok
        if result['department'][:2] in r['course_dpm_abbr'] and "選修" in r['is_required']:
            if r['grade'] >= 60:
                accumulated_elective += r['course_units']

        # --- 通識課程 ok
        if r['course_group'] in liberal_list:
            if r['grade'] >= 60:
                liberal_credit += r['course_units']

        if "英文（一）" in r['course_name'] and r['semester'] == 1 and int(r['grade']) >= 60:
            basic_course += 2
        elif "英文（一）" in r['course_name'] and r['semester'] == 2 and int(r['grade']) >= 60:
            basic_course += 2
        elif "英文（二）" in r['course_name'] and r['semester'] == 1 and int(r['grade']) >= 60:
            basic_course += 2
        elif "英文（二）" in r['course_name'] and r['semester'] == 2 and int(r['grade']) >= 60:
            basic_course += 2
        elif "Q" in r['course_group'] and r['semester'] == 1 and int(r['grade']) >= 60:
            basic_course += 2
        elif "Q" in r['course_group'] and r['semester'] == 2 and int(r['grade']) >= 60:
            basic_course += 2
        if "大學學習" in r['course_name'] and "通過" in r['grade']:
            basic_course += 1
        if "中國語文能力表達" in r['course_name'] and int(r['grade']) >= 60:
            basic_course += 2
        if "入門課程" in r['course_name'] and int(r['grade']) >= 60:
            basic_course += 1/3
        elif "活動參與" in r['course_name'] and "通過" in r['grade']:
            basic_course += 1/3
        elif "活動執行" in r['course_name'] and "通過" in r['grade']:
            basic_course += 1/3

    free_elective = total_graduation_credit - total_required_credit - total_elective_credit

    department_require = {
        "total_credits":          math.floor(total_credits),
        "graduation_credit":      total_graduation_credit,
        "required_credit":        total_required_credit,
        "elective_credit":        total_elective_credit,
        "free_elective":          free_elective,
        "accumulated_required":   math.floor(accumulated_required),
        "accumulated_elective":   accumulated_elective,
        "basic_course":           math.floor(basic_course),
        "liberal_credit":         liberal_credit
    }

    return department_require


def cal_basic_course(sessionid):
    result = loadfile(sessionid)

    club = 0

    basic_course = {
        'foreign_lang':     0,
        'chinese_lang':     0,
        'college_learn':    0,
        'club_learning':    0,
    }

    for r in result['grades']:
        if "英文（一）" in r['course_name'] and r['semester'] == 1 and int(r['grade']) >= 60:
            basic_course['foreign_lang'] += 2
        elif "英文（一）" in r['course_name'] and r['semester'] == 2 and int(r['grade']) >= 60:
            basic_course['foreign_lang'] += 2
        elif "英文（二）" in r['course_name'] and r['semester'] == 1 and int(r['grade']) >= 60:
            basic_course['foreign_lang'] += 2
        elif "英文（二）" in r['course_name'] and r['semester'] == 2 and int(r['grade']) >= 60:
            basic_course['foreign_lang'] += 2
        elif "Q" in r['course_group'] and r['semester'] == 1 and int(r['grade']) >= 60:
            basic_course['foreign_lang'] += 2
        elif "Q" in r['course_group'] and r['semester'] == 2 and int(r['grade']) >= 60:
            basic_course['foreign_lang'] += 2

        if "大學學習" in r['course_name'] and "通過" in r['grade']:
            basic_course['college_learn'] += 1
        if "中國語文能力表達" in r['course_name'] and int(r['grade']) >= 60:
            basic_course['chinese_lang'] += 2

        if "入門課程" in r['course_name'] and int(r['grade']) >= 60:
            club += 1/3
        elif "活動參與" in r['course_name'] and "通過" in r['grade']:
            club += 1/3
        elif "活動執行" in r['course_name'] and "通過" in r['grade']:
            club += 1/3

    basic_course['club_learning'] = math.floor(club)

    return basic_course


def cal_liberal_group(sessionid):
    result = loadfile(sessionid)

    liberal_course = {
        'humanities': 0,
        'sociology': 0,
        'science': 0
    }

    humanities_group = ['L', 'P', 'V', 'M']
    sociology_group = ['T', 'R', 'W', 'S']
    science_group = ['O', 'Z', 'U']

    for r in result['grades']:
        if r['course_group'] in humanities_group and int(r['grade']) >= 60:
            liberal_course['humanities'] += r['course_units']
        elif r['course_group'] in sociology_group and int(r['grade']) >= 60:
            liberal_course['sociology'] += r['course_units']
        elif r['course_group'] in science_group and int(r['grade']) >= 60:
            liberal_course['science'] += r['course_units']

    return liberal_course
