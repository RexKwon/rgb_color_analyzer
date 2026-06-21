import os
import time
import traceback

from PySide6.QtCore import QObject, Signal, Slot

from service.color_extractor import extract_colors
from service.color_compare import compare_colors
from model.analysis_result import AnalysisResult


class AnalysisWorker(QObject):

    progress = Signal(int, int)
    finished = Signal(object)
    error = Signal(str, str)
    completed = Signal()

    def __init__(
            self,
            file_list
    ):
        super().__init__()

        self.file_list = list(
            file_list
        )

    @Slot()
    def run(self):
        start_time = time.time()
        current_file_path = ""

        try:
            color_map = {}

            total_count = len(
                self.file_list
            )

            for idx, file_path in enumerate(
                    self.file_list,
                    start=1
            ):
                current_file_path = file_path

                self.progress.emit(
                    idx,
                    total_count
                )

                colors = extract_colors(
                    file_path
                )

                color_map[file_path] = colors

            common_colors, diff_colors = compare_colors(
                color_map
            )

            elapsed_time = round(
                time.time() - start_time,
                2
            )

            analysis_result = AnalysisResult.from_maps(
                color_map,
                common_colors,
                diff_colors,
                elapsed_time
            )

            self.finished.emit(
                analysis_result
            )

        except Exception:
            error_text = traceback.format_exc()

            if current_file_path:
                error_file_name = os.path.basename(
                    current_file_path
                )
            else:
                error_file_name = ""

            self.error.emit(
                error_file_name,
                error_text
            )

        finally:
            self.completed.emit()