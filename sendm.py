from twilio.rest import TwilioRestClient
 
# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = "AC73048884d9592024da0dee6ee9ce88a8"
auth_token  = "==Auth tokenn=="
client = TwilioRestClient(account_sid, auth_token)
 
message = client.messages.create(
	body="test message",
    to="+919910089606",    # Replace with your phone number
    from_="+15555555555") # Replace with your Twilio number
print message.sid