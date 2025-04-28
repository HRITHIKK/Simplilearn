from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# Global variable to store form data
stored_form_data = {}

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Webhook Receiver Running"})

# Webhook 1: Captures and stores form data and returns a custom button template message
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Received data:", data)

    # Safely extract form data
    form_data = data.get('metadata', {}).get('KM_CHAT_CONTEXT', {}).get('formData', {})
    if form_data:
        global stored_form_data
        stored_form_data = form_data
        print("Stored form data:", stored_form_data)

        # Personalized name fallback
        name = form_data.get('Name', 'there')
    else:
        name = "there"

    # Customized payload with button template
    return jsonify([{
        "message": f"Hi, {name}. which courses are you Intresded in? Below are a few courses that you may want to try",
        "platform": "kommunicate",
        "metadata": {
            "contentType": "300",
            "templateId": "6",
            "payload": [
                {
                    "title": "PMP Course",
                    "message": "PMP Course"
                },
                {
                    "title": "Data Analytics course",
                    "message": "Data Analytics course"
                },
                {
                    "title": "Cyber Security",
                    "message": "Cyber Security"
                }
            ]
        }
    }]), 200

# Webhook 2: Sends WhatsApp message and responds to bot
@app.route('/send_personalized_message', methods=['POST'])
def send_personalized_message():
    if not stored_form_data:
        return jsonify([{"message": "No form data available. Please submit the form first."}]), 400

    name = stored_form_data.get('Name')
    phone_number = stored_form_data.get('Phone_number')

    if name and phone_number:
        formatted_number = f"whatsapp:+91{phone_number[-10:]}"  # Ensure correct format

        # Prepare and send the API request
        api_url = 'https://services.kommunicate.io/rest/ws/message/campaign/send'
        headers = {
            'Api-Key': 'g9b5dzXiQ8xEWPfJqtazzdhP0r40alpu',
            'Content-Type': 'application/json',
            'Of-User-Id': 'devashish@kommunicate.io'
        }

        payload = {
            "messagePxyList": [
                {
                    "message": "Template Preview",
                    "metadata": {
                        "WHATSAPP_TEMPLATE": json.dumps({
                            "template": {
                                "name": "simplilearn",
                                "language": {
                                    "policy": "deterministic",
                                    "code": "EN"
                                },
                                "components": [
                                    {
                                        "type": "body",
                                        "parameters": [
                                            # Optional template parameters here
                                        ]
                                    }
                                ]
                            }
                        }),
                        "skipBot": True
                    },
                    "type": 5,
                    "contentType": 0,
                    "key": "payswl",
                    "platformSender": "whatsapp:+919606849266",
                    "platformName": "WHATSAPPDIALOG360",
                    "source": 1
                }
            ],
            "usernames": [formatted_number]
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload)
            print("API Response Status:", response.status_code)
            print("API Response Body:", response.text)
        except Exception as e:
            print("Error calling external API:", e)

        return jsonify([{"message": "We have reached out over Whatsapp"}]), 200
    else:
        return jsonify([{"message": "Form data is incomplete."}]), 400

if __name__ == '__main__':
    app.run(port=5001, debug=True)
