from collections.abc import Callable
from typing import Any


def wait_for(func: Callable, *args: Any, tries: int = 10, **kwargs: Any) -> Any:
    for _ in range(tries):
        try:
            result = func(*args, **kwargs)
            assert result is not None, 'Data not ready, retrying...'
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


def compare_texts(text1: str, text2: str):
    return strip_text(text1) == strip_text(text2)
