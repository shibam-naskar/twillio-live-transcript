from distutils.log import error
from twilio.rest import Client
import audioop
import base64
import json
import os
from flask import Flask, request
from flask_sock import Sock, ConnectionClosed
from twilio.twiml.voice_response import VoiceResponse, Start
from twilio.rest import Client
import vosk



TWILIO_ACCOUNT_SID = "AC729164347f96f726d0562c2767c4d31b"
TWILIO_AUTH_TOKEN = "b4560799e26a0a923b5325c6bc69e1c6"



app = Flask(__name__)
sock = Sock(app)
twilio_client = Client(TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN)
model = vosk.Model('model')

CL = '\x1b[0K'
BS = '\x08'


@app.route('/call', methods=['POST'])
def call():
    """Accept a phone call."""
    try:
        response = VoiceResponse()
        start = Start()
        start.stream(url=f'wss://{request.host}/stream')
        response.append(start)
        response.say('In the next 60 secounds what you will speak will be live transcripted')
        response.pause(length=60)
        print(f'Incoming call from {request.form["From"]}')
        return str(response), 200, {'Content-Type': 'text/xml'}
    except error:
        print(error)


@sock.route('/stream')
def stream(ws):
    """Receive and transcribe audio stream."""
    rec = vosk.KaldiRecognizer(model, 16000)
    while True:
        message = ws.receive()
        packet = json.loads(message)
        if packet['event'] == 'start':
            print('Streaming starting')
        elif packet['event'] == 'stop':
            print('\nStreaming stopped')
        elif packet['event'] == 'media':
            audio = base64.b64decode(packet['media']['payload'])
            audio = audioop.ulaw2lin(audio, 2)
            audio = audioop.ratecv(audio, 2, 1, 8000, 16000, None)[0]
            if rec.AcceptWaveform(audio):
                r = json.loads(rec.Result())
                print(CL + r['text'] + ' ', end='\n', flush=True)
            else:
                r = json.loads(rec.PartialResult())
                print(CL + r['partial'] + BS * len(r['partial']), end='', flush=True)


if __name__ == '__main__':
    from pyngrok import ngrok
    port = 5000
    public_url = ngrok.connect(port, bind_tls=True).public_url
    number = twilio_client.incoming_phone_numbers.list()[0]
    number.update(voice_url=public_url + '/call')
    print(f'Waiting for calls on {number.phone_number}')

    app.run(port=port)
