import json
import re
from typing import List, Optional


class DemoEditor:
    """
    An editor for asciinema recordings.

    :params input_file: The file path to the original recording to edit.
    :params output_file: The file path to the final demo.
    :params time_delta: The time delta used between each output.
    :params header: The asciinema header json. If not set read from recording.
    """

    def __init__(
        self,
        input_file: str,
        output_file: str,
        time_delta: float,
        header: Optional[dict],
    ) -> None:
        self.input_file = input_file
        self.output_file = output_file
        self.time_delta = time_delta
        self.header = header or {}
        self.outputs: List[str] = []
        with open(self.input_file, "r") as file:
            # Create header
            for k, v in json.loads(file.readline()).items():
                self.header.setdefault(k, v)
            # Create outputs
            for line in file.readlines():
                output = re.search(r'\[.*, "o", "(.*)"]', line)
                if output:
                    self.outputs.append(output.group(1))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback) -> None:  # dead: disable
        with open(self.output_file, "w") as file:
            # Write header
            file.write(f"{json.dumps(self.header)}\n")
            # Write outputs
            file.writelines(
                f'[{index * self.time_delta}, "o", "{output}"]\n'
                for index, output in enumerate(self.outputs, start=1)
            )
            # Write new line and wait for a second
            file.write(f'[{len(self.outputs) * self.time_delta + 1}, "o", "\\r\\n"]\n')


if __name__ == "__main__":
    with DemoEditor(
        input_file="assets/json/demo_output.json",
        output_file="assets/json/demo_full.json",
        time_delta=0.1,
        header=dict(height=20, width=100, timestamp=0),
    ) as demo_editor:
        # Insert cursor
        cursor = (
            "\\u001b[K\\u001b[J\\u001b[1;32m❯\\u001b[0m \\u001b[K\\r\\u001b[C\\u001b[C"
        )
        demo_editor.outputs.insert(0, cursor)
        # Insert command
        command = input("Enter command: ")
        for index, char in enumerate(command, start=1):
            demo_editor.outputs.insert(index, char)
        # Insert new line
        demo_editor.outputs.insert(len(command) + 1, "\\r\\n")
