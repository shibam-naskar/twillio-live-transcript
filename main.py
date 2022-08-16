import os
from twilio.rest import Client

account_sid = "AC729164347f96f726d0562c2767c4d31b"
auth_token = "b4560799e26a0a923b5325c6bc69e1c6"
client = Client(account_sid, auth_token)

call = client.calls.create(
                        twiml='<Response><Say>Ahoy, World!</Say></Response>',
                        to='+919064176535',
                        from_='+18554217378'
                    )

print(call.sid)