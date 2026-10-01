import pytest
from main import process_user_order_complex


def test_process_order_success_vip():
    # Основний успішний сценарій для VIP
    user = {"is_active": True, "is_vip": True}
    cart = {"items": ["item1"], "total": 600.0}
    result = process_user_order_complex(user, cart, promo_code="SALE2026")

    assert result["status"] == "success"
    assert result["discount"] == 0.30  # 0.25 VIP + 0.05 Promo
    assert result["final_price"] == 420.0


def test_process_order_user_inactive():
    # неактивний користувач
    user = {"is_active": False, "is_vip": False}
    cart = {"items": ["item1"], "total": 100.0}
    result = process_user_order_complex(user, cart)

    assert result["status"] == "error"
    assert result["message"] == "User is inactive"


def test_process_order_empty_cart():
    # порожній кошик
    user = {"is_active": True, "is_vip": False}
    cart = {"items": [], "total": 0.0}
    result = process_user_order_complex(user, cart)

    assert result["status"] == "error"
    assert result["message"] == "Cart is empty"