def getvalue(values, field_name):
    items = [item['Value'] for item in values if item['Key'] == field_name]
    return items[0] if items else None
