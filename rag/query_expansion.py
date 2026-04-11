def expand_query(query):
    expansions = {
        "vượt đèn đỏ": "không chấp hành tín hiệu đèn giao thông",
        "nồng độ cồn": "vi phạm nồng độ cồn khi lái xe"
    }

    for k, v in expansions.items():
        if k in query:
            return query + " " + v

    return query