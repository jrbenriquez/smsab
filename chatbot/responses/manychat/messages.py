from rest_framework.exceptions import ValidationError


TEXT = 'text'
IMAGE = 'image'
VIDEO = 'video'
AUDIO = 'audio'
FILE = 'file'
CARDS = 'cards'
BUTTON = 'button'
CARD_ELEMENTS = "card_elements"

BUTTON_TYPES = ["call", "url", "flow", "node", "buy"]

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
            "image_url": "https://placeimg.com/640/480/any",
            "action_url": "",
            "buttons": []
          }
        ],
        "image_aspect_ratio": "horizontal"
      },
    CARD_ELEMENTS: {
            "title": "Card title",
            "subtitle": "",
            "image_url": "https://placeimg.com/640/480/any",
            "action_url": "",
            "buttons": []
    },
    BUTTON: {
            "type": "url",
            "caption": "External link",
            "url": "https://manychat.com",
          }
}


def get_messages_format(key):
    return messages_format[key].copy()


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


def create_card_data(title, subtitle=None, image_url=None, action_url=None):
    text_template = get_messages_format(CARD_ELEMENTS)
    text_template['title'] = title
    text_template['title'] = title
    if subtitle:
        text_template['subtitle'] = subtitle
    if image_url:
        text_template['image_url'] = image_url
    if action_url:
        text_template['action_url'] = action_url

    return text_template


def add_button_to_element(element, button_type="url", caption=None, *args, **kwargs):
    if button_type not in BUTTON_TYPES:
        raise Exception(f'Invalid Button type: {button_type}')
    button_data = {}

    button_data["type"] = button_type
    if button_type == "url":
        url = kwargs.get('url')
        if not url:
            raise ValidationError('url required for button type "url"')
        button_data["caption"] = caption
        button_data['url'] = url
        button_data["webview_size"] = "full"

    elif button_type == "flow":
        target = kwargs.get('target')
        if not target:
            raise ValidationError('target required for button type "flow"')
        button_data["caption"] = caption
        button_data["target"] = target
    else:
        raise ValidationError('Button type not yet supported')

    button_list = list(element.get('buttons', []))
    button_list.append(button_data)

    element['buttons'] = button_list

    return element


def add_message_text(response_data, message, button_data=None):
    current_data = response_data.copy()
    current_messages = get_message_from_data(current_data)

    new_message_block = get_messages_format(TEXT)

    new_message_block["text"] = message

    if button_data:
        for data in button_data:
            button_type = data.get('button_type')
            caption = data.get('caption')
            url = data.get('url')

            if any([not button_type, not caption, not url]):
                raise ValidationError(
                    f'One of these could be blank: button_type {button_type}, caption {caption}, url {url}')

            new_message_block = add_button_to_element(
                new_message_block, button_type=button_type,
                caption=caption, url=url)

    response_data = append_messages(current_data, current_messages, new_message_block)

    return response_data


def add_message_gallery(response_data, gallery_list):
    current_messages = get_message_from_data(response_data)
    message_block = get_messages_format(CARDS)

    message_block['elements'] = gallery_list

    current_messages.append(message_block)

    response_data['content']['messages'] = current_messages

    return response_data


def add_message_card(response_data, title, subtitle=None, image_url=None, action_url=None):
    current_messages = get_message_from_data(response_data)
    message_block = get_messages_format(CARDS)

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
