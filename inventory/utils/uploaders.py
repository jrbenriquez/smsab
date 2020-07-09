def upload_item_photo(instance, filename):
    import os
    ext = filename.split('.')[-1]
    folder_name = "photos/{}/".format(instance.item.id)
    filename = "photo_{}.{}".format(instance.created_at, ext)
    return os.path.join(folder_name.replace(' ', ''), filename)


def upload_event_photo(instance, filename):
    import os
    ext = filename.split('.')[-1]
    folder_name = "events/{}/photos/".format(instance.event.id)
    filename = "photo_{}.{}".format(instance.created_at, ext)
    return os.path.join(folder_name.replace(' ', ''), filename)


