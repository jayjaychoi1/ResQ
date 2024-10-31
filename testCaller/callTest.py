# PROCESS
# user runs app -> twilio calls user -> user receives -> twilio redirect user to xml-dial-number (119 in our app)

# TO DO
# apply media stream
# apply VAD

# WORKING ON
# building xml file and deploy it in django to implement redirection to xml-dial-number

from twilio.rest import Client

account_sid = "AC9b60d2ccd19db8a02ce918d4989a7849"
auth_token = "71cdc967f7d3a2dd593b31c4ce4fc8a0"
client = Client(account_sid, auth_token)

call = client.calls.create(
    from_="+18582076378",
    to="+821063461851",
    url="http://demo.twilio.com/docs/voice.xml",
)

print(call.sid)