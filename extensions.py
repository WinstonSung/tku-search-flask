import base64
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def decode_base64(entext):
    b64_id = base64.b64decode(entext)
    return b64_id.decode("UTF-8")


def sendRecommendEmail(name, email, msg):
    content = MIMEMultipart()                           # 建立MIMEMultipart物件
    content["subject"] = "意見回饋"                      # 郵件標題
    content["from"] = "408630977@gms.tku.edu.tw"        # 寄件者
    content["to"] = "408630977@gms.tku.edu.tw"          # 收件者

    message = "■ From：%s 先生/小姐\n" \
              "■ 連絡方式：%s\n" \
              "■ 建議訊息：%s" % (name, email, msg)

    content.attach(MIMEText(message))    # 郵件內容

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login("408630977@gms.tku.edu.tw", "hlmdrtgicxgyoour")  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
        except Exception as e:
            print("Error message: ", e)


def convertStrToJson(seesionid):
    fname = 'static/api/' + seesionid + '.json'
    file = open(fname, "r")
    g = file.read()
    return json.loads(g)
