import imaplib  # For IMAP email protocol support

# Email server configuration
imap_ssl_host = 'imap.gmail.com'  # Can be changed to 'imap.mail.yahoo.com' for Yahoo mail
imap_ssl_port = 993  # Standard IMAP SSL port
username = 'user@gmail.com'
password = 'pass'   

# Connect to email server using SSL
imap = imaplib.IMAP4_SSL(imap_ssl_host, imap_ssl_port)
imap.login(username, password)

# Select the Inbox folder
imap.select('Inbox')

# Search for all emails in the inbox
tmp, data = imap.search(None, 'ALL')

# Process the first email found
for num in data[0].split():
	# Fetch the email content
	tmp, data = imap.fetch(num, '(RFC822)')
	print('Message: {0}\n'.format(num))
	print(data[0][1])
	break  # Process only the first email

# Close the connection
imap.close()
