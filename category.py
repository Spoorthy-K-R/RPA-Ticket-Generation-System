import nltk  
import csv   
import re    
import random  

# List of important words that help in categorizing emails
# These words are used as features for classification
important_words = [
    'kudos', 'love', 'commending', 'great', 'nice', 'congratulate', 'good', 'super', 'cool',
    'bad', 'angry', 'sad',
    'expectations', 'improve', 'know', 'suggest', 'happy', 'commendable', 'recommend',
    'awesome', 'applaudable', 'appreciate', 'glad'
]

# Define the possible categories for email classification
categories = ['appreciation', 'suggestion', 'complaint', 'request', 'enquiry']

# Add category names to important words for better classification
important_words += categories

def categorize_feature(email):
    """
    Extracts features from an email for classification.
    
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
        result['mail_has({})'.format(word)] = word.lower() in sub_words or word.lower() in body_words

    # Check if any category name appears in subject words
    for category in sub_words:
        if (category in categories):
            result['guessed_categ'] = category

    return result

# Load and prepare training data
csv_filename = 'RPA_DATASET.csv'
csv_file = open(csv_filename, mode='r')
train_set = []

# Read training data from CSV file
for row in list(csv.DictReader(csv_file)):
    # Create tuple of (email_data, category) for each row
    train_set.append((
        {
            'body': row['Body (FROM MAIL)'],
            'subject': row['Subject (FROM MAIL)']
        },
        row['CATEGORY']
    ))
csv_file.close()

# Generate feature set for training
# Convert each email into features using categorize_feature function
feature_set = [(categorize_feature(email), categ) for (email, categ) in train_set]

# Shuffle the training data for better model performance
random.shuffle(feature_set)

# Train the Naive Bayes classifier using the feature set
category_classifier = nltk.classify.NaiveBayesClassifier.train(feature_set)

