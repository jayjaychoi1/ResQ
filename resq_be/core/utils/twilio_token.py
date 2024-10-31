import os
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant

# 환경변수 또는 직접 입력된 Twilio 설정값
account_sid = ''
api_key = ''
api_secret = ''
outgoing_application_sid = ''

def create_twilio_access_token(identity):
    # Access Token 생성
    token = AccessToken(account_sid, api_key, api_secret, identity=identity)

    # Voice Grant 추가
    voice_grant = VoiceGrant(outgoing_application_sid=outgoing_application_sid, incoming_allow=True)
    token.add_grant(voice_grant)

    return token.to_jwt()