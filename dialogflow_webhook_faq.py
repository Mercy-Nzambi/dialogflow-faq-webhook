
from flask import Flask, request, jsonify
import csv
import difflib
import os

app = Flask(__name__)

# Load FAQ from CSV
faq_data = {}

def load_faq(file_path='/Users/adrian/dialogflowbase/agriculture_faq_kids.csv'):
    print("Looking for:", os.path.abspath(file_path))
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            question = row['Question'].strip().lower()
            answer = row['Answer'].strip()
            faq_data[question] = answer

load_faq()

def find_best_answer(user_input):
    user_input = user_input.strip().lower()
    questions = list(faq_data.keys())
    match = difflib.get_close_matches(user_input, questions, n=1, cutoff=0.6)
    if match:
        return faq_data[match[0]]
    else:
        return "I'm not sure, but I'm still learning about that!"

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(force=True)

    # Extract user's message from Dialogflow CX request
    user_input = req.get("fulfillmentInfo", {}).get("tag", "")
    text_input = req.get("text", "")
    if not text_input:
        # Fallback if text is nested in sessionInfo
        text_input = req.get("sessionInfo", {}).get("parameters", {}).get("any", "")

    # Search FAQ and get response
    response_text = find_best_answer(text_input)

    # Format response for Dialogflow CX
    return jsonify({
        "fulfillment_response": {
            "messages": [
                {
                    "text": {
                        "text": [response_text]
                    }
                }
            ]
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
