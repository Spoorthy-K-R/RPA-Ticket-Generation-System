import smtplib
from email.message import EmailMessage

# Define required information for different types of requests
# Format: 'Subject': [(['field_name', 'alternative_name'], regex_pattern), ...]
requirements = {
    'Baggage Related': [
        (['pnr'], r"(\d[\- ]?){10}"),  # PNR number pattern
        (['bag color', 'color'],)  # Bag color information
    ],
    'Refund': [
        (['pnr'], r"(\d[\- ]?){10}"),  # PNR number
        (['train name', 'train'],),  # Train name
        (['origin', 'from'],),  # Origin station
        (['destination', 'to'],),  # Destination station
        (['mobile no','mobile number','mobile','phone'], r"[+]?(\d[\- ]?){10,13}"),  # Contact number
        (['card no', 'card number', 'card'], r"(\d[\- ]?)+"),  # Card number
        (['booking id', 'transaction id', 'referance id', 'referance no'],),  # Booking reference
        (['refund amount', 'amount'],)  # Refund amount
    ],
    'Special Assistance': [
        (['pnr'], r"(\d[\- ]?){10}"),  # PNR number
        (['destination', 'to'],),  # Destination station
        (['origin', 'from'],)  # Origin station
    ]
}

def send_mail(mail, ticket):
    """
    Sends a response email to the customer based on their ticket.
    
    Args:
        mail (str): Recipient's email address
        ticket (dict): Ticket information containing category, subject, and status
    """
    # Set up email parameters
    sender = 'support@bookticket.com'
    receivers = [mail]

    # Create email message
    msg = EmailMessage()
    msg.set_content(generate_mail(ticket))

    # Set email subject
    msg['Subject'] = "RE: " + ticket['response_list'][0]['content']['subject']
    
    # Connect to SMTP server and send email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login("USERNAME@gmail.com", "PASSWORD")
    server.sendmail(sender, receivers, msg.as_string())
    server.quit()
    
def generate_mail(ticket):
    """
    Generates the content of the response email based on ticket information.
    
    Args:
        ticket (dict): Ticket information containing category, subject, and status
        
    Returns:
        str: Formatted email content
    """
    # Add ticket information header
    cat_info = "\n\nToken ID: {0}\nCATEGORY: {1}\nSUBJECT: {2}".format(
        ticket['token_id'],
        ticket['category'],
        ticket['subject']
    )
    
    # Generate appropriate message based on ticket status and category
    str1 = "We have received your mail\nIt will be processed shortly.\n"
    
    if (ticket['status'] == 1):
        # Message for incomplete information
        str1 = "We have received your mail but it seems some details are missing or wrong.\nPlease send those details.\n"
        for r_feat in ticket['required_details']:
            if not(r_feat[0][0] in ticket['features'].keys()):
                if (r_feat[0][0] == 'pnr'):
                    str1 += "\n" + r_feat[0][0].upper()
                else:
                    str1 += "\n" + r_feat[0][0].title()
    elif (ticket['category'] == 'Appreciation'):
        # Message for appreciation emails
        str1 = "We are glad to hear you liked our services and we hope that you will recommend us to your family and friends"
    elif (ticket['category'] == 'Suggestion'):
        # Message for suggestion emails
        str1 = "Thank you for your suggestion, we appreciate your effort and will try to implement in the best way possible"
    
    # Return complete email content
    return str1 + cat_info + "\nCheers"
