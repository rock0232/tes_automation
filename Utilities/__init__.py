import logging
from pathlib import Path

def get_project_root() -> Path:
    return Path(__file__).parent.parent

class Logger:
    @staticmethod
    def logen():
        path = get_project_root()
        logging.basicConfig(filename=f'{path}/Logs//automation.log',
                            format='%(asctime)s: %(levelname)s: %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p', force=True, level=logging.INFO)
        logger = logging.getLogger()
        return logger


my_dict = {
    'a': 1,
    'b': 2,
    'c': 3,
    'd': 4
}

# Filter values greater than 2
filtered_dict = dict(filter(lambda item: item[1] > 2, my_dict.items()))

print(filtered_dict)
