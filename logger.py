import functools
from multiprocessing import Process, Queue, Value
import time
import numpy as np


class Logger:
    def __init__(self) -> None:
        self._perf_max = Value("d", 0.0)
        self._perf_total = Value("d", 0.0)
        self._perf_num_calls = Value("d", 0.0)
        self._headers = [
            "fun_name",
            "call_time",
            "exec_time",
            "output",
            "args",
            "kwargs",
        ]
        self._separator = "|"
        self._supported_types = (int, np.ndarray, float, complex, str, list)

    def set_dump_cell(self, dump_queue: Queue):
        self._dump_queue = dump_queue

    def format(
        self, desired_headers, fun_name, call_time, exec_time, output, *args, **kwargs
    ):
        arguments = locals()

        data = []
        for header in self._headers:
            if header in desired_headers:
                item = arguments[header]
                if header == "args":
                    item = self._validate(item)
                if header == "output":
                    item = self._validate(item)
                data.append(item)
            else:
                data.append("_")
        # print(data)
        return data

    def _validate(self, lst):
        if type(lst) is tuple:
            result = []
            for item in lst:
                if isinstance(item, self._supported_types):
                    if type(item) == np.ndarray:
                        result.append(item.tolist())
                    else:
                        result.append(item)
                else:
                    result.append(str(type(item)))
            return result
        else:
            if isinstance(lst, self._supported_types):
                return lst
            else:
                return str(type(lst))

    def dump(self, data: str):
        self._dump_queue.put(data)

    def log(
        self, headers=["fun_name", "call_time", "exec_time", "output", "args", "kwargs"]
    ):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                exec_time = end_time - start_time

                self.dump(
                    self.format(
                        headers,
                        func.__name__,
                        start_time,
                        exec_time,
                        result,
                        *args,
                        **kwargs,
                    )
                )

                dump_time = time.time() - end_time
                self._update_performance(dump_time)
                return result

            return wrapper

        return decorator

    def _update_performance(self, dump_time):
        self._perf_total.value += dump_time
        self._perf_max.value = max(self._perf_max.value, dump_time)
        self._perf_num_calls.value += 1

    def get_logger_performance(self):
        print(
            " max dump time {} [s]\n mean dump time {} [s]\n num calls {}\n".format(
                self._perf_max.value,
                self._perf_total.value / self._perf_num_calls.value,
                self._perf_num_calls.value,
            )
        )


logger = Logger()
logger.set_dump_cell(Queue())
