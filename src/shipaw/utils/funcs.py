import time
from collections.abc import Callable
from datetime import date, datetime
from typing import Any


def wait_for(
    func: Callable, *args: Any, tries: int = 10, wait_for_type: type = Any, is_not_none: bool = True, **kwargs
) -> Any:
    for _ in range(tries):
        time.sleep(1)
        try:
            result = func(*args, **kwargs)
            if is_not_none:
                assert result is not None, 'Data not ready, retrying...'
            if wait_for_type is not Any:
                assert isinstance(result, wait_for_type), f'Expected type {wait_for_type}, got {type(result)}'
            return result
        except AssertionError:
            continue
    raise RuntimeError(f'Data not ready after {tries} retries')


# def wait_for[T: Any](func: Callable[Any, T], *args, tries=10) -> T:
#     for i in range(tries):
#         try:
#             return_data = func(*args)
#             assert return_data is not None, 'Data not ready , retrying...'
#             return return_data
#         except AssertionError:
#             pass
#     raise RuntimeError(f'Data not ready after {tries} retries')
def strip_text(text: str):
    return text.replace(' ', '').lower()


def compare_texts(text1: str, text2: str, ignore_case: bool = True, ignore_whitespace: bool = True) -> bool:
    text1 = text1.lower() if ignore_case else text1
    text2 = text2.lower() if ignore_case else text2
    text1 = text1.replace(' ', '') if ignore_whitespace else text1
    text2 = text2.replace(' ', '') if ignore_whitespace else text2
    return text1 == text2


def date_to_datetime(d: date) -> datetime:
    return datetime.combine(d, datetime.min.time())
