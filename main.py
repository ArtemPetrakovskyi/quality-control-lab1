def calculate_discount(price, customer_type):
    if price <= 0:
        return 0

    if customer_type == "VIP":
        return price * 0.2
    elif customer_type == "Regular":
        return price * 0.05
    else:
        return 0


print(calculate_discount(100, "VIP"))