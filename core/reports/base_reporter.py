"""Abstract Base Reporter — all reporters implement this."""
from abc import ABC, abstractmethod
import os


class BaseReporter(ABC):

    def __init__(self, config: dict):
        self.config = config
        self.output_dir = config.get("output_dir", "reports/output")
        os.makedirs(self.output_dir, exist_ok=True)

    @abstractmethod
    def generate(self, suite_result) -> str:
        """Generate report from SuiteResult. Returns output file path."""
