from pathlib import Path

from loguru import logger


def unused_path(filepath: Path):
    def numbered_filepath(filey: Path, number: int):
        new_stem = f'{filey.stem}_{number}'
        return filey.with_stem(new_stem)

    incremented = 1
    lpath = numbered_filepath(filepath, incremented)
    while lpath.exists():
        incremented += 1
        logger.warning(f'FilePath {lpath} already exists')
        lpath = numbered_filepath(filepath, incremented)
    logger.debug(f'Using FilePath={lpath}')
    return lpath
