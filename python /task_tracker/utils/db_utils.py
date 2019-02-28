import datetime


def save_to_db(data, model, additional_data = {}, remove_fields = []):
    if additional_data:
        data.update(additional_data)

    default = ['csrf_token']
    for key in remove_fields + default:
        data.pop(key, None)

    db_obj = model(data)
    db_obj.save()
    return db_obj

