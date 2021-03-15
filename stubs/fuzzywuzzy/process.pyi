from typing import Union, Iterable, Any, List, Tuple


def extract(query:str, choices: Iterable, processor: Any=None, scorer: Any=None, limit: int=0) -> List: ...

def extractOne(query: str, choices: Iterable, processor: Any=None, scorer: Any=None, score_cutoff: int=0) -> Tuple: ...