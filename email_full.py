# Import required modules
from category import *  # For email categorization
from subject_detection import *  # For subject classification
from send_email import *  # For sending response emails
from feature_extraction import *  # For extracting features from emails
import easyimap  # For email fetching
import time  # For adding delays

# Global variables for ticket management
tickets = []  # List to store all active tickets
token_id = 10000  # Starting ID for ticket numbering

def extract_and_store_info(email, ticket):
    """
    Processes an email and updates the corresponding ticket with extracted information.
    
    Args:
        email (dict): Dictionary containing email subject and body
        ticket (dict): Dictionary containing ticket information
        
    Returns:
        dict: Result containing processed information
    """
    result = {}
    
    # Classify email if not already classified
    if not('category' in ticket.keys()):
        ticket['category'] = category_classifier.classify(categorize_feature(email))
        ticket['subject'] = subject_classifier.classify(subject_feature(email))
    
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
    
    # Extract required details from email body
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
    
    # Add response to history
    ticket['response_list'].append(result)

    # Print ticket information
    print(ticket['token_id'])
    print(ticket['category'], " : ", ticket['subject'])
    
    return result

# Main loop for email processing
while(1):
    time.sleep(3)  # Wait 3 seconds between checks
    
    # Connect to email server
    imapper = easyimap.connect('imap.gmail.com','USERNAME@gmail.com', 'PASSWORD')
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
            try:
                ticket['required_details'] = requirements[ticket['subject']]
            except:
                ticket['required_details'] = []
            tickets.append(ticket)

        # Process email and update ticket
        extract_and_store_info(mail_content, ticket)
        # Send response email
        send_mail(mail_id, ticket)
