from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

def load_approved_numbers(file_path='approved_numbers.txt'):
    with open(file_path) as f:
        return [line.strip() for line in f if line.strip()]
    
approved_numbers = load_approved_numbers()

@app.route("/", methods=['POST'])
def sms_reply():
    """Respond to incoming messages with a simple text message."""
    # Get the message the user sent
    incoming_msg = request.form.get('Body').strip()
    from_number = request.form.get('From')

    resp = MessagingResponse()
    # Check if the sender's number is approved and the message is "Christmas"
    if from_number in approved_numbers and incoming_msg.lower() == "christmas":
        resp.message("Merry Christmas!")
        return str(resp)
    elif from_number in approved_numbers and incoming_msg.lower() == "subscribe":
        resp.message("You are now subscribed!")
        return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)