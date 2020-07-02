import smtplib
import os, sys, glob
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate


def get_latest_file(path, *paths):
    """Returns the name of the latest (most recent) file
    of the joined path(s)"""
    fullpath = os.path.join(path, *paths)
    list_of_files = glob.glob(fullpath)  # You may use iglob in Python3
    if not list_of_files:                # I prefer using the negation
        return None                      # because it behaves like a shortcut
    latest_file = max(list_of_files, key=os.path.getctime)
    _, filename = os.path.split(latest_file)
    return filename

def send_mail(send_from, send_to, subject, text, files=None,
              server=None):
    assert isinstance(send_to, list)

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)


    server = smtplib.SMTP('email-smtp.us-west-2.amazonaws.com', 587)
    server.connect("email-smtp.us-west-2.amazonaws.com", 2587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login("AKIA6IVFV4KGC6JLWNG7", "BFqhinfbsgc+SjcspKfhxvjUDnNqS8/b/yXaafN9UrAc")
    server.sendmail(send_from, send_to, msg.as_string())
    server.close()

def send_attachment(outfile='test_results'):
    pwd = os.getcwd()
    htmlfile = get_latest_file(pwd, 'reports','reports', '2020*.html')
    print('htmlfile=', htmlfile)
    htmltime, ext = os.path.splitext(htmlfile)
    htmlpath = os.path.join(pwd, 'reports','reports', htmlfile)
    if not os.path.isfile(outfile):
        print('====>>> No such file %s' % outfile)
    if not os.path.isfile(htmlpath):
        print('====>>> No such file %s' % htmlpath)
    mfrom = 'notifications@smartcasttv.com'
    mto = ['<gracetestsense@gmail.com>']
    subject = 'Test Results: %s_%s' % (outfile,htmltime)
    text = 'result attached.'
    send_mail(mfrom, mto, subject, text, files=[outfile, htmlpath])
    print('email %s sent' % subject)

if __name__ == '__main__':
    send_attachment(outfile=sys.argv[1])