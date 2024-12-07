from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from resq_be.core.config import conf_outgoing_application_sid, conf_twilio_api_secret, conf_twilio_api_key, conf_account_sid

account_sid = conf_account_sid
api_key = conf_twilio_api_key
api_secret = conf_twilio_api_secret
outgoing_application_sid = conf_outgoing_application_sid

# create Access token
def create_twilio_access_token(identity):

    token = AccessToken(account_sid, api_key, api_secret, identity=identity)
    token.ttl = 1200
    voice_grant = VoiceGrant(outgoing_application_sid=outgoing_application_sid, incoming_allow=True)
    token.add_grant(voice_grant)

    return token.to_jwt()