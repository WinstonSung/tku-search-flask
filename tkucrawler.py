from datetime import datetime
import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from chromedriver_autoinstaller import *

from chromedriver_autoinstaller import *

from bs4 import BeautifulSoup

# --- 成績儲存路徑
api_path = 'static/api/'

# --- 目標網址
LOGIN_PAGE_URL = 'https://sso.tku.edu.tw/aissinfo/emis/TMW0000.aspx'
STUDENT_INFO_URL = 'https://sso.tku.edu.tw/aissinfo/emis/tmw0012.aspx'
HISTORY_GRADE_URL = 'https://sso.tku.edu.tw/aissinfo/emis/TMWS100.aspx'
GRADE_REQUIRE_URL = 'https://sso.tku.edu.tw/aissinfo/emis/TMWC120.aspx'

# --- 密碼錯誤msg
ERROR_MSG_en = 'Authentication fail. Account or password entered incorrectly, please re-enter'
ERROR_MSG_zh = '帳號或密碼輸入錯誤，請重新輸入'


def autoGetGradeAndStdInfo(sid, spw):
    install()
    fname = api_path + sid + '.json'

    # --- Driver基本參數設定
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    driver.get(LOGIN_PAGE_URL)
    driver.implicitly_wait(20)  # --- 每個元素最多尋找20秒，超過則出錯

    time.sleep(1.8)
    student_id = driver.find_element_by_name("username")  # --- 尋找學號輸入框
    student_pw = driver.find_element_by_name("password")  # --- 尋找密碼輸入框
    student_id.send_keys(sid)  # --- 填入學號
    student_pw.send_keys(spw)  # --- 填入密碼

    time.sleep(0.4)
    login_btn = driver.find_element_by_name("loginbtn")
    login_btn.click()

    current_page_html = driver.page_source
    if current_page_html.find(ERROR_MSG_en) != -1 or current_page_html.find(ERROR_MSG_zh) != -1:
        logging.error("輸入密碼錯誤")
        return 901  # --- 輸入密碼錯誤
    else:
        if not os.path.isdir(api_path):  # --- 如果成績的資料夾不存在，就新增一個資料夾
            os.mkdir(api_path)

        driver.get(STUDENT_INFO_URL)
        driver.get(GRADE_REQUIRE_URL)

        # --- 獲得學生姓名、系級、學號
        department = driver.find_element(By.XPATH, '/html/body/form/center/font[1]').get_attribute("innerHTML")
        student_id = driver.find_element(By.XPATH, '/html/body/form/center/font[2]').get_attribute("innerHTML")
        stud_name  = driver.find_element(By.XPATH, '/html/body/form/center/font[3]').get_attribute("innerHTML")

        std_info = {
            'name':  stud_name.strip(),   # --- 「學生姓名」
            'dpt':   department.strip(),  # --- 「系級」
            'id':    student_id.strip()   # --- 「學號」
        }

        # --- 獲得畢業審核學年度、畢業學分數、必修學分數，本系選修課最低學分
        require_arr = driver.find_element(By.XPATH, '//*[@id="Form1"]/center/font[4]/b').get_attribute("innerText")

        require_arr = require_arr.split('　')
        require_arr = [r.split('：')[1] for r in require_arr]

        require = {
            'entered_year':  int(require_arr[0]),  # --- 「入學年」：106,107,108...
            'grad_credit':   int(require_arr[1]),  # --- 「畢業學分」
            'required':      int(require_arr[2]),  # --- 「系必修」
            'elective':      int(require_arr[3])   # --- 「系選修」
        }

        driver.get(HISTORY_GRADE_URL)
        # --- 抓歷史成績 -----------------------------------
        allgrades = driver.find_element(By.XPATH, '//*[@id="Form1"]/center/table/tbody/tr[2]/td/table/tbody').get_attribute("outerHTML")
        allgrades = BeautifulSoup(allgrades, "html.parser").find_all("tr")

        grades = []

        for g in allgrades[1:-2]:
            course_name = str(g.find_all("td")[5]).replace("<br/>", ",")
            course_name = BeautifulSoup(course_name, "html.parser")
            course_name = course_name.text.split(",")

            is_required = str(g.find_all("td")[8]).replace("<br/>", ",")
            is_required = BeautifulSoup(is_required, "html.parser")
            is_required = is_required.text.split(",")

            course_group = g.find_all("td")[7].text if g.find_all("td")[7].text.strip() != "" else "null"
            course_score = int(g.find_all("td")[10].text.strip()) if (g.find_all("td")[10].text.strip()).isdigit() else g.find_all("td")[10].text.strip()

            grades_dict = {
                "academic_year":     int(g.find_all("td")[0].text),     # --- 「學年」：106,107,108...
                "semester":          int(g.find_all("td")[1].text),     # --- 「學期」：1 or 2 上下學期
                "course_dpm_id":     g.find_all("td")[2].text,          # --- 「開課單位代碼」：資管TLMXB, 企管TLCXB...
                "course_dpm_abbr":   g.find_all("td")[3].text,          # --- 「開課單位簡稱」：TLMXB有可能是資管一, 資管二...
                "course_id":         g.find_all("td")[4].text,          # --- 「科號」：如果重修，代號相同就可抵銷
                "course_name":       course_name[0],                    # --- 「科目名稱」
                "course_name_en":    course_name[1],                    # --- 「科目名稱(英)」
                "semester_index":    g.find_all("td")[6].text,          # --- 「學期序」：若課程開上下兩學期，則1,2；只開一學期就0
                "course_group":      course_group,                      # --- 「群別」：通識、大學學習等等才有
                "is_required":       is_required[0],                    # --- 「必選修」
                "is_required_en":    is_required[1],                    # --- 「必選修(英)」
                "course_units":      int(g.find_all("td")[9].text),     # --- 「學分」
                "grade":             course_score                       # --- 「成績」
            }
            grades.append(grades_dict)

        currenttime = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        student_information = {
            "name":             std_info['name'],
            "student_id":       std_info['id'],
            "department":       std_info['dpt'],
            "requirement":      require,
            "grades":           grades,
            "last_modified":    currenttime
        }

        f = open(fname, "w")
        f.write(json.dumps(student_information, ensure_ascii=False))
        driver.quit()
