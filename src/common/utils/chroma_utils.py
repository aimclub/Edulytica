import ipaddress


def is_valid_chroma_collection_name(name: str) -> bool:
    if not (3 <= len(name) <= 63):
        return False

    if ".." in name:
        return False

    if not (name[0].islower() or name[0].isdigit()) or not (name[-1].islower() or name[-1].isdigit()):
        return False

    allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789._-"
    if not all(c in allowed_chars for c in name):
        return False

    try:
        ipaddress.ip_address(name)
        return False
    except ValueError:
        pass

    return True
