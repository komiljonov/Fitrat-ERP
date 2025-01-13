from flask import Flask, request, jsonify

from .models import Lid
app = Flask(__name__)

@app.route('/instagram-webhook', methods=['POST'])
def instagram_webhook():
    data = request.json  # Get the JSON payload from Albato
    print(f"data: {data}")
    if 'entry' in data:
        for entry in data['entry']:
            print(f"entry: {entry}")
            for messaging in entry.get('messaging', []):
                print(f"messaging: {messaging}")
                sender_id = messaging['sender']['id']
                message_text = messaging['message']['text']

                # Process the lead (e.g., save to DB)
                save_lead(sender_id, message_text)

    return jsonify({"status": "success"}), 200

def save_lead(sender_id, message_text):
    print(f"New Lead: {sender_id} - {message_text}")
    new_lid = Lid.objects.get_or_create(sender_id=sender_id, message_text=message_text)
    return new_lid


if __name__ == '__main__':
    app.run(port=5000)
