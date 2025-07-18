from category import *  
from subject_detection import *  
from send_email import *  
from feature_extraction import *  
from langchain_integration import categorize_email, validate_form_data, generate_response, suggest_priority
import easyimap  
import time  
import json

tickets = []  # List to store all active tickets
token_id = 10000  # Starting ID for ticket numbering

def extract_and_store_info(email, ticket):
    """
    Processes an email and updates the corresponding ticket with extracted information using LangChain.
    
    Args:
        email (dict): Dictionary containing email subject and body
        ticket (dict): Dictionary containing ticket information
        
    Returns:
        dict: Result containing processed information
    """
    result = {}
    
    # Classify email if not already classified using LangChain
    if not('category' in ticket.keys()):
        try:
            category_result = categorize_email(email)
            print('category_result')
            print(category_result)
            ticket['category'] = category_result['category']
            ticket['category_confidence'] = category_result['confidence']
            ticket['category_reasoning'] = category_result['reasoning']
        except Exception as e:
            print(f"Error in email categorization: {e}")
            # Fallback to old method
            ticket['category'] = category_classifier.classify(categorize_feature(email))
            ticket['subject'] = subject_classifier.classify(subject_feature(email))

    # Analyze sentiment using LangChain
    try:
        # sentiment_result = analyze_sentiment(email)
        # ticket['sentiment'] = sentiment_result['sentiment']
        # ticket['urgency_level'] = sentiment_result['urgency_level']
        # ticket['key_phrases'] = sentiment_result['key_phrases']
        ticket['sentiment'] = 'neutral'
        ticket['urgency_level'] = 'medium'
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        ticket['sentiment'] = 'neutral'
        ticket['urgency_level'] = 'medium'
    
    # Store email content
    result['content'] = email
    
    # Initialize features and response list if not present
    if (not ticket['features']):
        ticket['features'] = {}
    if (not ticket['response_list']):
        ticket['response_list'] = []
    
    # Get required details based on subject
    try:
        ticket['required_details'] = requirements[ticket['subject']]
    except:
        ticket['required_details'] = []
    
    # Use LangChain to validate and extract form data
    try:
        validation_result = validate_form_data(email, ticket)
        ticket['features'] = validation_result.get('extracted_info', {})
        ticket['missing_info'] = validation_result.get('missing_fields', [])
        ticket['validation_notes'] = validation_result.get('validation_notes', '')
        ticket['is_valid'] = validation_result.get('is_valid', False)
    except Exception as e:
        print(f"Error in form validation: {e}")
        # Fallback to old method
        for (x) in ticket['required_details']:
            if (len(x) > 1):
                feature = extract_feature(email['body'], x[0], x[1])
            else:
                feature = extract_feature(email['body'], x[0])
            if (feature):
                ticket['features'][x[0][0]] = feature

    # Update ticket status
    ticket['status'] = 1  # INFORMATION PENDING FROM CUSTOMER SIDE
    if (len(ticket['required_details']) == len(ticket['features'])):
        ticket['status'] = 2  # COMPLETE INFORMATION RECEIVED (PROCEEDED FOR HUMAN SUPPORT)

    # Suggest priority using LangChain
    try:
        priority_result = suggest_priority(ticket, {'sentiment': ticket['sentiment'], 'urgency_level': ticket['urgency_level']})
        ticket['priority'] = priority_result['priority']
        ticket['priority_reasoning'] = priority_result['reasoning']
    except Exception as e:
        print(f"Error in priority suggestion: {e}")
        ticket['priority'] = 'medium'

    # Generate response using LangChain
    try:
        response_content = generate_response(ticket)
        result['generated_response'] = response_content
    except Exception as e:
        print(f"Error in response generation: {e}")
        result['generated_response'] = None
    
    # Add response to history
    ticket['response_list'].append(result)

    # Print ticket information
    print(f"Token ID: {ticket['token_id']}")
    print(f"Category: {ticket['category']} (Confidence: {ticket.get('category_confidence', 'N/A')})")
    print(f"Subject: {ticket['subject']}")
    print(f"Sentiment: {ticket['sentiment']}")
    print(f"Priority: {ticket['priority']}")
    print(f"Status: {ticket['status']}")
    print(f"Missing Info: {ticket.get('missing_info', [])}")
    
    return result

while(1):
    time.sleep(3) 
    
    # Connect to email server
    imapper = easyimap.connect('imap.gmail.com','user@gmail.com', 'pass')
    mail_list = imapper.unseen(2)
    if (not mail_list):
        continue
    
    # Process new emails
    for mail_id in imapper.listids(limit=1):
        print("Found Mail")
        mail = imapper.mail(mail_id)

        # Extract email information
        mail_id = mail.from_addr
        mail_content = {'subject': mail.title, 'body':mail.body}

        # Initialize ticket
        ticket = {}
        
        # Check if ticket exists for this email address
        for t in tickets:
            if (mail_id == t['mail']):
                ticket = t
                break

        # Create new ticket if none exists
        if (not ticket):
            token_id += 1
            ticket['status'] = 0  # New ticket
            ticket['token_id'] = token_id
            ticket['mail'] = mail_id
            ticket['features'] = {}
            ticket['response_list'] = []
            ticket['subject'] = mail_content['subject']
            try:
                ticket['required_details'] = requirements[ticket['subject']]
            except:
                ticket['required_details'] = []
            tickets.append(ticket)

        # Process email and update ticket
        result = extract_and_store_info(mail_content, ticket)
        
        # Send response email
        if result.get('generated_response'):
            # Use the generated response from LangChain
            send_mail_with_custom_response(mail_id, ticket, result['generated_response'].get('text'))
        else:
            # Fallback to original send_mail function
            send_mail(mail_id, ticket)
