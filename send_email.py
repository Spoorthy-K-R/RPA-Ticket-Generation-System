import smtplib
from email.message import EmailMessage

# Define required information for different types of requests
# Format: 'Subject': [(['field_name', 'alternative_name'], regex_pattern), ...]
requirements = {
    'Baggage Related': [
        (['pnr'], r"(\d[\- ]?){10}"),  # PNR number pattern
        (['bag color', 'color'],) 
    ],
    'Refund': [
        (['pnr'], r"(\d[\- ]?){10}"),  
        (['train name', 'train'],), 
        (['origin', 'from'],),  
        (['destination', 'to'],),  
        (['mobile no','mobile number','mobile','phone'], r"[+]?(\d[\- ]?){10,13}"), 
        (['booking id', 'transaction id', 'referance id', 'referance no'],),  
        (['refund amount', 'amount'],)  
    ],
    'Special Assistance': [
        (['pnr'], r"(\d[\- ]?){10}"),  
        (['destination', 'to'],),  
        (['origin', 'from'],)  
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

def send_mail_with_custom_response(mail, ticket, custom_response):
    # Set up email parameters
    sender = 'support@bookticket.com'
    receivers = [mail]

    # Create email message
    msg = EmailMessage()
    
    # Add ticket information to the custom response
    enhanced_response = custom_response + f"\n\nToken ID: {ticket['token_id']}\nCATEGORY: {ticket['category']}\nSUBJECT: {ticket['subject']}\nCheers"
    msg.set_content(enhanced_response)

    # Set email subject
    msg['Subject'] = "RE: " + ticket['response_list'][0]['content']['subject']
    
    # Connect to SMTP server and send email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login("user@gmail.com", "pass")
    server.sendmail(sender, receivers, msg.get_content())
    server.quit()
    
def generate_mail(ticket):
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
        str1 = "We are glad to hear you liked our services and we hope that you will recommend us to your family and friends"
    elif (ticket['category'] == 'Suggestion'):
        str1 = "Thank you for your suggestion, we appreciate your effort and will try to implement in the best way possible"
    
    return str1 + cat_info + "\nCheers"
