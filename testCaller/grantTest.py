import os
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant

# required for all twilio access tokens
# To set up environmental variables, see http://twil.io/secure
account_sid = 'AC9b60d2ccd19db8a02ce918d4989a7849'
api_key = 'SK96ee304908f2441c297ce8944bf038e4'
api_secret = 'qdQ03lADDblQpntbD1xZ0BqINb5UebPH'

# required for Voice grant
outgoing_application_sid = 'AP6bfd4af5d54dfdb8ee7becbc99c407a8'
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