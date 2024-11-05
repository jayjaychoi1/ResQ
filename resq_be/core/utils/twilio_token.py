from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant

account_sid = ''
api_key = ''
api_secret = ''
outgoing_application_sid = ''

# create Access token
def create_twilio_access_token(identity):

    token = AccessToken(account_sid, api_key, api_secret, identity=identity)
    voice_grant = VoiceGrant(outgoing_application_sid=outgoing_application_sid, incoming_allow=True)
    token.add_grant(voice_grant)

    return token.to_jwt()