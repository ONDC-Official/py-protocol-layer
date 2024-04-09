def validate_sum_of_quote_breakup(payload):
    order_quote = payload["message"]["order"]["quote"]
    total_price = float(order_quote["price"]["value"])
    breakup_price = 0
    for p in order_quote["breakup"]:
        breakup_price += float(p["price"]["value"])

    if breakup_price == total_price:
        return None
    else:
        return f"Total price and sum of breakup are mismatch! {total_price} != {breakup_price}"
