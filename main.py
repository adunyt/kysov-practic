from mailbox import Mailbox
from typing import Reversible
from urllib import response
import eel
from imap_tools import MailBox, AND, A
from email.mime.text import MIMEText
import smtplib
import ssl

imap_servers = {
    "Yandex": {"server": "imap.yandex.ru",
               "port": 993},
    "Google": {"server": "imap.gmail.com",
               "port": 993},
}


smpt_servers = {
    "Yandex": {"server": "smtp.yandex.ru",
               "port": 465},
    "Google": {"server": "smtp.gmail.com",
               "port": 465},
    "Localhost": {"server": "localhost",
                  "port": 25},
}


@eel.expose
def contact_saver(contact: str) -> str:
    import json
    import os
    try:
        newContact = json.loads(contact)
        file = os.open("contacts.json", os.O_RDWR | os.O_CREAT)
        jsonFile: dict = json.load(file)
        contacts: list = jsonFile["contacts"]
        contacts.append(newContact)
        json.dump(contacts, file)
    except Exception as e:
        raise e
    finally:
        os.close(file)


@eel.expose
def getLetters(email, password, imap_name):
    imap_server = imap_servers[imap_name]
    with MailBox(imap_server["server"], imap_server["port"]).login(email, password) as mailbox:
        messages = mailbox.fetch()
        return messages


@eel.expose
def sendLetter(email: str, password: str, smtp_name: str, receivers: list, subject: str, message: str):
    smtp_server = smpt_servers[smtp_name]

    sender = email
    msg = MIMEText(message)

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receivers

    with smtplib.SMTP(smtp_server["server"], smtp_server["port"]) as server:
        try:
            server.login(email, password)
            server.sendmail(sender, receivers, msg.as_string())
            return {"status": "OK",
                    "error_message": None}
        except Exception as e:
            return {"status": "Error",
                    "error_message": e}


@eel.expose
def tryLogin(server_name, login, password):
    print("Start tryLogin...")
    jsonResponse = {}
    smtp = smpt_servers["Localhost"]
    imap = imap_servers[server_name]
    print("start with")
    try:
        with smtplib.SMTP_SSL(smtp["server"], smtp["port"]) as smtp_server:
            print("smtp ssl....")
            smtp_server.login(login, password)
            smtp_server.close()
            jsonResponse["smtp"] = {"status": "OK",
                                    "error_code": None}
    except ssl.SSLError:
        with smtplib.SMTP(smtp["server"], smtp["port"]) as smtp_server:
            print("smtp....")
            smtp_server.login(login, password)
            smtp_server.close()
            jsonResponse["smtp"] = {"status": "OK",
                                    "error_code": None}
    except Exception as e:
        jsonResponse["smtp"] = {"status": "Error",
                                "error_code": e}

    with MailBox(imap["server"], imap["port"]) as imap_server:
        print("imap....")
        try:
            imap_server.login(login, password)
            jsonResponse["imap"] = {"status": "OK",
                                    "error_code": None}
        except Exception as e:
            jsonResponse["imap"] = {"status": "Error",
                                    "error_code": e}

    return jsonResponse


try:
    # getLetters("endercat1357@yandex.ru", "gymtnwklohdpqsvd")
    print(tryLogin("Yandex", "endercat1357@yandex.ru", "gymtnwklohdpqsvd"))
    eel.init("web")
    eel.start("index.html")
except Exception as e:
    import ctypes
    ctypes.windll.user32.MessageBoxW(0, str(e), "Ошибка!", 0)

# TODO:
# калькулятор
