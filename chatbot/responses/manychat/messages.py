TEXT = 'text'
IMAGE = 'image'
VIDEO = 'video'
AUDIO = 'audio'
FILE = 'file'
CARDS = 'cards'

messages_format = {
    TEXT: {
        "type": TEXT,
        "text": ""
    }
}


message_types = [
    TEXT,
    IMAGE,
    VIDEO,
    AUDIO,
    FILE,
    CARDS,

]


def add_message_text(response_data, message):
    current_messages = response_data['content']['messages']
    text_template = messages_format[TEXT]

    text_template["text"] = message

    current_messages.append(text_template)

    response_data['content']['messages'] = current_messages

    return response_data
