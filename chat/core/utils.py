from datetime import datetime


DT_FORMAT = "%Y-%m-%d %H:%S:%M"


def dt_to_str(dt: datetime) -> str:
    return dt.strftime(DT_FORMAT)


def str_to_dt(dt_str: str) -> datetime:
    return datetime.strptime(dt_str, DT_FORMAT)
