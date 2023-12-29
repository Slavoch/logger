from logger import Logger
import os
import numpy as np
from datetime import datetime


class SCV_Dumper:
    def __init__(self, logger: Logger, dir_path="./logs") -> None:
        self._dump_queue = logger._dump_queue
        self._headers = logger._headers
        self._separator = logger._separator
        self.path = dir_path

    def decode(self, items):
        data = []
        for item in items:
            if type(item) == str:
                data.append(item)
            elif type(item) == np.ndarray:
                data.append(np.array2string(item, separator=", "))
            else:
                data.append(str(item))
        return data

    def dump_loop(self, echo=False):
        file_name = "logs_" + datetime.now().strftime("%d_%m_%Y_%H:%M:%S") + ".csv"
        path = os.path.join(self.path, file_name)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        file = open(path, "w")
        file.writelines(self._separator.join(self._headers))
        file.write("\n")
        file.close()
        while True:
            file = open(path, "a")
            if not self._dump_queue.empty():
                items = self._dump_queue.get()
                items = self.decode(items)
                if echo:
                    print(f"Processing {items}")
                file.writelines(self._separator.join(items))
                file.write("\n")
            file.close()
