def is_eligible(user:dict,rules:dict|None=None)->bool:
    if not rules:return True
    for key,allowed in rules.items():
        if key in user and isinstance(allowed,list) and user[key] not in allowed:return False
    return True
