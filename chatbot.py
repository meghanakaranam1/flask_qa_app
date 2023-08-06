from flask import Flask, render_template, request

app = Flask(__name__)

# Maintain a list to store chat history
chat_history = []

responses = {
    "hi": "Hi!, How can I assist you today?",
    "hello": "Hi there! How can I support you today?",
    "how are you": "I'm an AI, so I don't have feelings, but I'm here to listen to you.",
    "bye": "Take care! Remember, I'm here whenever you need to talk.",
    "feeling anxious": "I'm here to help. When you're anxious, try taking deep breaths and focusing on the present moment.",
    "feeling sad": "I'm here to help. When you're sad, try taking deep breaths and focusing on the present moment.",
    "lonely": "You're not alone. Reach out to friends, family, or a support group when you're feeling lonely.",
    "depressed": "It's okay to feel down. Consider engaging in activities you enjoy or talking to a professional.",
    "suicidal thoughts": "I'm really sorry to hear that, but I can't provide the help you need. Please talk to a mental health professional or a helpline.",
    "coping strategies": "When you're stressed, practicing mindfulness and relaxation techniques can be helpful.",
    "seeking help": "While I'm here to chat, it's important to consult a mental health expert for personalized guidance.",
    "self-care": "Taking care of yourself is important. Make sure you're getting enough rest, eating well, and staying hydrated.",
    "challenging times": "Life can be tough, but you have the strength to overcome challenges.",
    "positive affirmations": "Repeat positive affirmations to boost your mood and self-esteem.",
    "therapy": "Therapy can be a valuable resource. Consider speaking with a therapist who can provide specialized support.",
    "reaching out": "Don't hesitate to reach out to a trusted friend or family member when you need to talk.",
    "progress": "Every step forward, no matter how small, is a step in the right direction.",
    "default": "Sorry, could You please elaborate."
}


def get_bot_response(user_input):
    user_input = user_input.lower()
    for keyword in responses:
        if keyword in user_input:
            return responses[keyword]
    return responses["default"]

@app.route('/chat', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_message = request.form.get('user_message')
        if user_message.strip() != "":
            bot_response = get_bot_response(user_message)
            chat_history.append({"user": user_message, "bot": bot_response})

    return render_template('chatbot.html', chat_history=chat_history)

if __name__ == '__main__':
    app.run(debug=True)
