def process_orders(orders, user_role, is_active, has_discount, region):
    result = []
    if is_active:
        if user_role == "admin" or user_role == "manager":
            for order in orders:
                if order > 0:
                    if region == "US":
                        if has_discount:
                            result.append(order * 0.8)
                        else:
                            result.append(order * 0.9)
                    elif region == "EU":
                        if has_discount:
                            result.append(order * 0.75)
                        else:
                            result.append(order * 0.85)
                else:
                    print("Invalid order")
    return result

def process_orders_duplicate(orders, user_role, is_active, has_discount, region):
    result = []
    if is_active:
        if user_role == "admin" or user_role == "manager":
            for order in orders:
                if order > 0:
                    if region == "US":
                        if has_discount:
                            result.append(order * 0.8)
                        else:
                            result.append(order * 0.9)
                    elif region == "EU":
                        if has_discount:
                            result.append(order * 0.75)
                        else:
                            result.append(order * 0.85)
                else:
                    print("Invalid order")
    return result