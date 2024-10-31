import os
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant

# required for all twilio access tokens
# To set up environmental variables, see http://twil.io/secure
account_sid = ''
api_key = ''
api_secret = ''

# required for Voice grant
outgoing_application_sid = ''
identity = 'user'

# Create access token with credentials
token = AccessToken(account_sid, api_key, api_secret, identity=identity)

# Create a Voice grant and add to token
voice_grant = VoiceGrant(
    outgoing_application_sid=outgoing_application_sid,
    incoming_allow=True, # Optional: add to allow incoming calls
)
token.add_grant(voice_grant)

# Return token info as JSON
print(token.to_jwt())