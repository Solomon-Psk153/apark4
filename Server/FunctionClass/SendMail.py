import smtplib  # SMTP 사용을 위한 모듈
import re  # Regular Expression을 활용하기 위한 모듈
from email.mime.multipart import MIMEMultipart  # 메일의 Data 영역의 메시지를 만드는 모듈
from email.mime.text import MIMEText  # 메일의 본문 내용을 만드는 모듈
from email.mime.image import MIMEImage  # 메일의 이미지 파일을 base64 형식으로 변환하기 위한 모듈
import secrets, string # 난수, 문자열 값들을 조회하기 위한 모듈

class MailProvider(object):
    def __init__(self, dest, subject, code):
        self.dest=dest
        self.subject=subject
        self.code=code
    
    def sendMail(self):
        
        gmailSmtpServer = "smtp.gmail.com"
        gmailPort = 465
        myAccount = "psk153777@gmail.com"
        myPassword = "fznl rudj ndua wihu"
        
        smtp = smtplib.SMTP_SSL(gmailSmtpServer, gmailPort)
        smtp.login(myAccount, myPassword)
        
        msg = MIMEMultipart()
        msg['Subject'] = self.subject
        msg['From'] = myAccount
        msg['To'] = self.dest
        
        body = self.ContentTemplate(
                self.subject, 
                self.code
            )
        msg.attach(MIMEText(body, 'html'))
        
        try:
            smtp.sendmail(myAccount, self.dest, msg.as_string())
            return {'message': 'send exist email success'}, 200
        except smtplib.SMTPDataError as e:
            return {'message': 'check does email accepted, server policy, email setting'}, 550
        except Exception as e:
            return {'message': 'email not found:{}'.format(e)}, 404
            
    @classmethod
    def randomCodeCreator(cls, type):
        
        if type in ['register', 'password']:
            characters = (type == 'password') * string.ascii_uppercase + string.digits
            
            return ''.join(secrets.choice(characters) for _ in range(6 if type == 'register' else 8))
    
    def ContentTemplate(self, title, randomCode):
        return """
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            background-color: #ffffff;
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        .header {{
            font-size: 20px;
            text-align: center;
            color: #333;
            margin-bottom: 20px;
        }}
        .code {{
            font-size: 24px;
            letter-spacing: 3px;
            display: flex;
            justify-content: center;
            margin: 20px auto;
        }}
        .code span {{
            padding: 10px;
            margin: 0 2px;
            font-weight: bold;
        }}
        .c1 {{ background-color: navy; color: lime; }}
        .c2 {{ background-color: darkblue; color: lightgreen; }}
        .c3 {{ background-color: mediumblue; color: palegreen; }}
        .c4 {{ background-color: blue; color: yellowgreen; }}
        .c5 {{ background-color: royalblue; color: springgreen; }}
        .c6 {{ background-color: deepskyblue; color: greenyellow; }}
        .footer {{
            font-size: 12px;
            text-align: center;
            color: #999;
            margin-top: 20px;
        }}
        </style>
        </head>
        <body>
        <div class="container">
            <div class="header">
            {}
            </div>
            <p>안녕하세요,</p>
            <p>귀하의 코드는 아래와 같습니다:</p>
            <div class="code">
            {}
            </div>
            <p>이 코드를 앱에 입력해 주세요.</p>
            <div class="footer">
            © 2024 Recycle Mate. All rights reserved.
            </div>
        </div>
        </body>
        </html>""".format(title, randomCode)
        
        # https://www.tempmail.us.com/ko/python-and-javascript/google-%EC%96%B4%EC%8B%9C%EC%8A%A4%ED%84%B4%ED%8A%B8%EA%B0%80-pdf-%EC%9D%B8%EB%B3%B4%EC%9D%B4%EC%8A%A4%EB%A5%BC-%EC%9E%98%EB%AA%BB-%ED%95%B4%EC%84%9D%ED%95%98%EB%8A%94-%EA%B2%83%EC%9D%84-%EB%B0%A9%EC%A7%80