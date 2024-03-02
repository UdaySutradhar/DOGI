import spacy
from textblob import TextBlob
from gensim.summarization import keywords 
import random
import requests

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Define responses for different intents
responses = {
    "greeting": ["Hello!", "Hi there!", "Hey! How can I assist you?"],
    "farewell": ["Goodbye!", "See you later!", "Take care!"],
    "thanks": ["You're welcome!", "No problem!", "My pleasure!"],
    "time": ["It's time to seize the day!", "Time flies when you're having fun!", "Time waits for no one!"],
    "weather": ["The weather is {weather} today.", "It's {weather} outside right now.", "Expect {weather} weather today."],
    "default": ["I'm sorry, I don't understand.", "Can you please rephrase that?", "I'm still learning."]
}

def extract_named_entities(text):
    """Extract named entities from the input text."""
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

def extract_keywords(text):
    """Extract keywords using TextRank algorithm."""
    kw = keywords(text, ratio=0.1).split('\n')
    return kw

def get_intent(text):
    """Identify the intent based on named entities, sentiment, and keywords."""
    doc = nlp(text)
    sentiment = TextBlob(text).sentiment.polarity
    if sentiment > 0.5:
        return "thanks"
    elif sentiment < -0.5:
        return "farewell"
    for token in doc:
        if token.ent_type_ == "TIME":
            return "time"
        elif token.ent_type_ == "GPE":
            return "weather"
    return None

def generate_response(intent, context=None):
    """Generate a response based on the identified intent and context."""
    if intent in responses:
        return random.choice(responses[intent])
    elif intent == "topic":
        return "Sure, I can help you with that. What specific topic are you interested in?"
    elif intent == "search":
        if context:
            return f"Here are some resources related to {context}."
        else:
            return "I'm sorry, I couldn't find any relevant resources."
    else:
        return random.choice(responses["default"])

def fetch_weather(city):
    """Fetch weather information from an external API."""
    api_key = "your_api_key"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_desc = data['weather'][0]['description']
        return weather_desc
    else:
        return "Weather information is not available at the moment."

def dialogue_manager():
    """Multi-turn dialogue manager."""
    print("Welcome! I'm your advanced virtual assistant.")
    context = None

    while True:
        user_input = input("You: ").strip()

        # Extract named entities, keywords, and identify intent
        named_entities = extract_named_entities(user_input)
        keywords = extract_keywords(user_input)
        intent = get_intent(user_input)

        # Update context based on intent
        if intent == "topic":
            context = keywords[0] if keywords else None
        elif intent == "search":
            context = None

        # Generate response
        if intent == "weather" and named_entities:
            city = next((entity[0] for entity in named_entities if entity[1] == "GPE"), None)
            if city:
                weather = fetch_weather(city)
                response = generate_response(intent).format(weather=weather)
            else:
                response = generate_response("default")
        else:
            response = generate_response(intent, context)

        print("Assistant:", response)

if __name__ == "__main__":
    dialogue_manager()
