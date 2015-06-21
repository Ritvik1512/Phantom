import time, threading
import requests
import subprocess
import smtplib

def send_mail(data):
  fromaddr = 'piedpiper.angelhack@gmail.com'
  toaddrs  = 'mavidser@gmail.com'
  msg = data
  username = 'piedpiper.angelhack@gmail.com'
  password = 'redmiones'
  server = smtplib.SMTP('smtp.gmail.com:587')
  server.ehlo()
  server.starttls()
  server.login(username,password)
  server.sendmail(fromaddr, toaddrs, msg)
  server.quit()

def scan_for_changes(url):
  print 'heh'
  changes = requests.post('http://localhost:5000/check', data={'url':url}).text
  print changes

  if changes=='No Change':
    pass
  else:
    subprocess.Popen(['notify-send', 'Changes occurerd in '+url])
    message = 'Subject: %s\n\n%s' % ('Changes occurerd in '+url, changes)
    send_mail(message)

  threading.Timer(5, scan_for_changes, [url]).start()
  return

# scan_for_changes('http://localhost:8000/')
