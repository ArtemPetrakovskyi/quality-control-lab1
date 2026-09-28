def calculate_discount(price: float, is_vip: bool) -> float:
    """Обчислює підсумкову ціну з урахуванням знижки."""
    if price <= 0:
        return 0.0

    discount = 0.20 if is_vip else 0.05
    return price * (1.0 - discount)


if __name__ == "__main__":
    total = calculate_discount(100.0, True)
    print(f"Total price: {total}")