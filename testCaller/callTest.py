# PROCESS
# user runs app -> twilio calls user -> user receives -> twilio redirect user to xml-dial-number (119 in our app)

# TO DO
# apply media stream
# apply VAD

# WORKING ON
# building xml file and deploy it in django to implement redirection to xml-dial-number

from twilio.rest import Client

account_sid = ""
auth_token = ""
client = Client(account_sid, auth_token)

call = client.calls.create(
    from_="+",
    to="+",
    url="",
)

print(call.sid)