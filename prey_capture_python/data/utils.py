from datetime import datetime


def datetime_str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d_%H_%M_%S")