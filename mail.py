import smtplib
fromaddr = 'piedpiper.angelhack@gmail.com'
toaddrs  = 'mavidser@gmail.com'
msg = 'Why,Oh why!'
username = 'piedpiper.angelhack@gmail.com'
password = 'redmiones'
server = smtplib.SMTP('smtp.gmail.com:587')
server.ehlo()
server.starttls()
server.login(username,password)
server.sendmail(fromaddr, toaddrs, msg)
server.quit()
