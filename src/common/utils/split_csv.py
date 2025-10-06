from typing import Optional, List


def split_csv(val: Optional[str]) -> List[str]:
    if not val:
        return []
    raw = [x.strip() for x in val.replace("\n", ",").split(",")]
    return [x[:-1] if x.endswith("/") else x for x in raw if x]
