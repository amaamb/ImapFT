import imaplib

#copy from
from_server = {'server': 'imap.example.com',
               'username': 'j@example.com',
               'password': 'pass',
               'box_names': ['Inbox', 'Sent']}

#copy to
to_server = {'server': '2.2.2.2',
             'username': 'archive',
             'password': 'password',
             'box_name': 'Inbox'}

def connect_server(server):
#    conn = imaplib.IMAP4(server['server'])  #without SSL
    conn = imaplib.IMAP4_SSL(server['server']) #with SSL
    conn.login(server['username'], server['password'])
    print 'Logged into mail server @ %s' % server['server']
    return conn

def disconnect_server(server_conn):
    out = server_conn.logout()

if __name__ == '__main__':
    From = connect_server(from_server)
    To = connect_server(to_server)

    for box in from_server['box_names']:
        box_select = From.select(box, readonly = False)  #open box which will have its contents copied
        print 'Fetching messages from \'%s\'...' % box
        resp, items = From.search(None, 'ALL')  #get all messages in the box
        msg_nums = items[0].split()
        print '%s messages to archive' % len(msg_nums)

        for msg_num in msg_nums:
            resp, data = From.fetch(msg_num, "(FLAGS INTERNALDATE BODY.PEEK[])") # get email
            message = data[0][1] 
            flags = imaplib.ParseFlags(data[0][0]) # get flags
            flag_str = " ".join(flags)
            date = imaplib.Time2Internaldate(imaplib.Internaldate2tuple(data[0][0])) #get date
            copy_result = To.append(to_server['box_name'], flag_str, date, message) # copy to archive

            if copy_result[0] == 'OK': 
                del_msg = From.store(msg_num, '+FLAGS', '\\Deleted') # mark for deletion

        ex = From.expunge() # delete marked
        print 'expunge status: %s' % ex[0]
        if not ex[1][0]: # result can be ['OK', [None]] if no messages need to be deleted
            print 'expunge count: 0'
        else:
            print 'expunge count: %s' % len(ex[1])

    disconnect_server(From)
    disconnect_server(To)