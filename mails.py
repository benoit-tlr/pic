import imaplib
import ssl
import email
import sys

server = 'email.isae.fr'

f = open('creds.txt')
u = f.readline().strip()
p = f.readline().strip()
f.close()

print("Connecting to servers...", end='')
ctx = ssl.create_default_context()
ctx.set_ciphers('DEFAULT')
imap = imaplib.IMAP4_SSL(server, 993, ssl_context=ctx)

print('OK\nLogging in...', end='')
r = imap.login(u, p)
if r[0] == 'OK':
    print('OK')
else:
    print()
    print("Error: " + str(r[0]))
    exit(1)

imap.select('Inbox')
result, data = imap.search(None, 'ALL')

i = len(data[0].split())

def get_mail(x):
    uid = data[0].split()[x]
    try:
        result, email_data = imap.fetch(uid, '(RFC822)')
        raw_email = email_data[0][1]
        email_message = email.message_from_string(raw_email.decode('utf-8'))
    except:
        return None, 0
    ts = sys.getsizeof(raw_email)
    return email_message, ts

def list_mails(start, stop):
    ts = 0
    for x in range(max(start, 0), min(stop, i)):
        email_message, tss = get_mail(x)
        ts += tss
        if email_message == None:
            print(str(x) + ": SKIPPED")
            continue
        subject = str(email.header.make_header(email.header.decode_header(email_message['Subject'])))
        print(str(x) + ": " + str(subject))
        print("Size: " + str(ts))

list_mails(0, 999)
