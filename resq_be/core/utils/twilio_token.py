from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant

account_sid = 'AC9b60d2ccd19db8a02ce918d4989a7849'
api_key = 'SK96ee304908f2441c297ce8944bf038e4'
api_secret = 'qdQ03lADDblQpntbD1xZ0BqINb5UebPH'
outgoing_application_sid = 'AP878b3724bb6543b0bc49eec88c232d17'

# create Access token
def create_twilio_access_token(identity):

    token = AccessToken(account_sid, api_key, api_secret, identity=identity)
    # time limit for demo
    token.ttl = 1200
    voice_grant = VoiceGrant(outgoing_application_sid=outgoing_application_sid, incoming_allow=True)
    token.add_grant(voice_grant)

    return token.to_jwt()