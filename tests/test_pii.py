from app.pii import scrub_text, scrub_value


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_supported_vietnamese_pii() -> None:
    text = (
        "Phone 0987 654 321, CCCD 012345678901, "
        "card 4111 1111 1111 1111, passport B1234567"
    )
    out = scrub_text(text)
    assert "0987" not in out
    assert "012345678901" not in out
    assert "4111" not in out
    assert "B1234567" not in out
    assert "REDACTED_PHONE_VN" in out
    assert "REDACTED_CCCD" in out
    assert "REDACTED_CREDIT_CARD" in out
    assert "REDACTED_PASSPORT" in out


def test_scrub_nested_values() -> None:
    value = {
        "message": "student@vinuni.edu.vn",
        "items": ["Call 0987654321", {"detail": "CCCD 012345678901"}],
    }
    safe = scrub_value(value)
    rendered = str(safe)
    assert "student@" not in rendered
    assert "0987654321" not in rendered
    assert "012345678901" not in rendered


def test_scrub_does_not_modify_correlation_id() -> None:
    correlation_id = "req-e1234567"
    assert scrub_text(correlation_id) == correlation_id
