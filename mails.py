import imaplib
import ssl
import email
import sys
from fuzzywuzzy import fuzz

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
    res = []
    for x in range(max(start, 0), min(stop, i)):
        print("Current: " + str(x), end='\r')
        email_message, ts = get_mail(x)
        if email_message == None:
            print('\r' + str(x) + ": SKIPPED")
            continue
        subject = str(email.header.make_header(email.header.decode_header(email_message['Subject'])))
        res.append((ts, subject))
    return res

res = list_mails(0, 9999)
matchesres = []
blacklist = []
for i in range(len(res)):
    matches = [res[i]]
    if res[i] in blacklist: continue
    blacklist.append(res[i])
    for j in range(len(res)):
        if i == j: continue
        percent = fuzz.ratio(res[i][1], res[j][1])
        if percent > 65:
            blacklist.append(res[j])
            matches.append((percent, res[j]))
    matchesres.append(matches)

totalsize = 0
for x in matchesres:
    if len(x) <= 1: continue
    print("----- MATCH -----")
    print(x[0][1] + " (" + str(x[0][0]) + " KiB)")
    totalsize += x[0][0]
    for i in range(1, len(x)):
        print(str(x[i][0]) + "% : " + x[i][1][1] + " (" + str(x[i][1][0]) + " KiB)")
        totalsize += x[i][1][0]
    print("\n\n")
print("Total size: " + str(totalsize // 1024) + " KiB")
