from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from utils import fetch_reply

'''
sample messages:show information of qutub minar
send photos of qutub minar
get my preferences


'''

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/sms", methods=['POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Fetch the message
    print(request.form)
    msg = request.form.get('Body')

    # Create reply
    sender=request.form.get("From")
    resp = MessagingResponse()
    temp=fetch_reply(msg,sender)
    if type(temp)==str:
        resp.message(temp)
    else:
        print(temp[0])
        resp.message("").media(temp[0])

    print(resp)
    return str(resp)



if __name__ == "__main__":
    app.run(debug=True)
