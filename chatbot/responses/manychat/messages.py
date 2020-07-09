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
    },
    CARDS: {
        "type": CARDS,
        "elements": [
          {
            "title": "Card title",
            "subtitle": "",
            "image_url": "",
            "action_url": "",
            "buttons": []
          }
        ],
        "image_aspect_ratio": "horizontal"
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


def get_message_from_data(response_data):
    if 'messages' in response_data['content']:
        current_messages = response_data['content']['messages']
    else:
        current_messages = []

    return current_messages


def append_messages(response_data, current_messages, message_block):
    current_messages.append(message_block)

    response_data['content']['messages'] = current_messages

    return response_data


def add_message_text(response_data, message):
    current_messages = get_message_from_data(response_data)
    text_template = messages_format[TEXT]

    text_template["text"] = message

    current_messages.append(text_template)

    response_data['content']['messages'] = current_messages

    return response_data


def add_message_card(response_data, title, subtitle=None, image_url=None, action_url=None):
    current_messages = get_message_from_data(response_data)
    message_block = messages_format[CARDS]

    if not title:
        raise Exception('Title is required for Cards')

    message_block['elements'][0]['title'] = title
    if subtitle:
        message_block['elements'][0]['subtitle'] = subtitle
    if image_url:
        message_block['elements'][0]['image_url'] = image_url
    if action_url:
        message_block['elements'][0]['action_url'] = action_url

    response_data = append_messages(response_data, current_messages, message_block)

    return response_data
