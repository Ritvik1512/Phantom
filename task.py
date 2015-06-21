import time, threading
import requests
import subprocess
import smtplib
from twilio.rest import TwilioRestClient 
 
# put your own credentials here 
def send_text(data):
  ACCOUNT_SID = "AC643827145bf34449eaed29541061cb61" 
  AUTH_TOKEN = "d95e4350d5c7a08dd74ba98ae3f6b4cf" 
   
  client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN) 
   
  client.messages.create(
    to="+918982896363", 
    from_="+19286123050", 
    body=data
  )


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
    send_text('Changes occurerd in '+url)

  threading.Timer(5, scan_for_changes, [url]).start()
  return

# scan_for_changes('http://localhost:8000/')
