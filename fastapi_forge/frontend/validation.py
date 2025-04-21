def raise_if_missing_fields(required: list[tuple[str, str | None]]):
    missing_required = [field_name for field_name, kwarg in required if not kwarg]
    if missing_required:
        msg = f"Missing fields: {', '.join(missing_required)}."
        raise ValueError(msg)
