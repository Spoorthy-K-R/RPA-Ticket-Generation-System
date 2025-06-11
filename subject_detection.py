# Import required libraries
import nltk  # Natural Language Toolkit for text processing
import csv   # For reading CSV files
import random  # For shuffling training data

# List of possible subjects for email classification
subjects = [
    "Baggage Related", "Staff Related", "Special Assistance", "Announcements",
    "Food", "Booking Issues", "Fare", "Website", "Delays OR Cancellation",
    "Call Center", "Refund", "Payment Failure", "New Train Request",
    "Request Documents", "Tatkaal", "Station", "Train Details", "Train Service"
]

# List of important words that help identify subjects
# These words are used as features for subject classification
important_words = [
    # Baggage related words
    'lost', 'bag', 'misplace', 'find',
    # Staff behavior words
    'misbehaviour', 'misconduct', 'rude', 'absent', 'behaviour', 'good', 'joyful',
    # Special assistance words
    'wheelchair', 'handicapped', 'senior', 'porter', 'cooli',
    # Food related words
    'tasty', 'food',
    # Technical issues
    'access', 'failure', 'payment',
    # Fare related words
    'cheap', 'expensive', 'high', 'fares',
    # Service quality words
    'helpful', 'irritated',
    # Urgency related
    'tatkaal', 'urgent',
    # Station and infrastructure
    'tidy', 'dirty', 'clean', 'infrastructure', 'busy',
    # Technical services
    'wifi', 'wi-fi',
    # Customer service
    'customer', 'care', 'call', 'disconnects', 'disconnected'
]

def subject_feature(email):
    """
    Extracts features from an email for subject classification.
    
    Args:
        email (dict): Dictionary containing 'subject' and 'body' of the email
        
    Returns:
        dict: Dictionary of features indicating presence of important words
    """
    # Split email into subject and body
    subject, body = email['subject'], email['body']
    
    # Tokenize subject and body into words
    sub_words = nltk.word_tokenize(subject.lower())
    body_words = nltk.word_tokenize(body.lower())
    
    # Initialize result dictionary
    result = {}

    # Check for presence of important words in either subject or body
    for word in important_words:
        result['has({})'.format(word)] = word in sub_words or word in body_words

    return result    

# Load and prepare training data
csv_filename = 'RPA_DATASET.csv'
csv_file = open(csv_filename, mode='r')
train_set = []

# Read training data from CSV file
for row in list(csv.DictReader(csv_file)):
    # Create tuple of (email_data, subject) for each row
    train_set.append((
        {
            'body': row['Body (FROM MAIL)'],
            'subject': row['Subject (FROM MAIL)']
        },
        row['REGARDING']
    ))
csv_file.close()

# Generate feature set for training
# Convert each email into features using subject_feature function
feature_set = [(subject_feature(email), categ) for (email, categ) in train_set]

# Shuffle the training data for better model performance
random.shuffle(feature_set)

# Train the Naive Bayes classifier using the feature set
subject_classifier = nltk.classify.NaiveBayesClassifier.train(feature_set)
