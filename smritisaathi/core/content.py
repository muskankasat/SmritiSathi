"""Spoken/quiz content shared by the games and the audio generator (single source of truth)."""
CK = {  # common-knowledge bank: (question, options, answer index)
 "en": [("Which festival is called the festival of lights?", ["Diwali", "Holi", "Eid", "Pongal"], 0),
        ("How many days are in a week?", ["5", "6", "7", "8"], 2),
        ("Which is India's national bird?", ["Parrot", "Peacock", "Crow", "Sparrow"], 1)],
 "hi": [("रोशनी का त्योहार किसे कहते हैं?", ["दिवाली", "होली", "ईद", "पोंगल"], 0),
        ("एक सप्ताह में कितने दिन होते हैं?", ["5", "6", "7", "8"], 2),
        ("भारत का राष्ट्रीय पक्षी कौन सा है?", ["तोता", "मोर", "कौआ", "चिड़िया"], 1)],
 "mr": [("दिव्यांचा सण कोणता?", ["दिवाळी", "होळी", "ईद", "पोंगल"], 0),
        ("आठवड्यात किती दिवस असतात?", ["५", "६", "७", "८"], 2),
        ("भारताचा राष्ट्रीय पक्षी कोणता?", ["पोपट", "मोर", "कावळा", "चिमणी"], 1)],
}
PERSONAL_Q = {
 "child": {"en": "What is your child's name?", "hi": "आपके बच्चे का नाम क्या है?", "mr": "तुमच्या मुलाचे नाव काय?"},
 "town":  {"en": "Where is your hometown?", "hi": "आपका गृहनगर कौन सा है?", "mr": "तुमचे गाव/शहर कोणते?"},
}
NAMES = ["Sunita", "Ramesh", "Meena", "Anil", "Kavita", "Prakash"]
TOWNS = ["Nagpur", "Pune", "Nashik", "Amravati", "Wardha", "Kolhapur"]

# Spoken form of digits (so the TTS says the number word, not a stray character)
DIGIT_WORDS = {
 "en": ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"],
 "hi": ["शून्य", "एक", "दो", "तीन", "चार", "पाँच", "छह", "सात", "आठ", "नौ"],
 "mr": ["शून्य", "एक", "दोन", "तीन", "चार", "पाच", "सहा", "सात", "आठ", "नऊ"],
}
