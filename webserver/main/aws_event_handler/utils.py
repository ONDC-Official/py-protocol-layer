import email
import re


def get_attachment_from_email_data(contents):
    msg = email.message_from_string(contents)
    attachment = msg.get_payload()[1]
    from_address = msg['from']
    regex = "\\<(.*?)\\>"
    from_address = re.findall(regex, from_address)[0]

    # Write the attachment to a temp location
    response = attachment.get_payload(decode=True)
    with open('/tmp/attach.xlsx', 'wb') as file:
        file.write(attachment.get_payload(decode=True))
    return "/tmp/attach.xlsx"


# if __name__ == '__main__':
#     content = open("/Users/navdeepagarwal/Downloads/fsfnm5roafgvtqstsc5d0eqlqkq7buj9uu3h8ag1").read()
#     get_attachment_from_email_data(content)
