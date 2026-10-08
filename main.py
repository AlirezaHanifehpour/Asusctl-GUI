import re
import sys
from pathlib import Path

from PySide6.QtCore import QProcess, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
    QColorDialog,
    QComboBox,
    QGridLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QWidget,
)


WIDTH = 460
HEIGHT = 250
INITIAL_COLOR = "#ffffff"

EFFECTS = [
    "static",
    "breathe",
    "rainbow-cycle",
    "rainbow-wave",
    "stars",
    "rain",
    "highlight",
    "laser",
    "ripple",
    "pulse",
    "comet",
    "flash",
]

PROFILES = [
    "Quiet",
    "Balanced",
    "Performance",
]

SPEED = "med"
RAINBOW_DIRECTION = "right"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Asusctl GUI")
        self.setFixedSize(WIDTH, HEIGHT)

        self.current_color = INITIAL_COLOR
        self.processes = set()

        self._setup_ui()
        self._apply_style()

        # Get the current profile when the application starts
        self._load_current_profile()

    def _setup_ui(self):
        widget = QWidget()
        self.setCentralWidget(widget)

        grid = QGridLayout(widget)
        grid.setAlignment(
            Qt.AlignmentFlag.AlignTop |
            Qt.AlignmentFlag.AlignLeft
        )

        color_label = QLabel("Backlight color")
        self.color_button = QPushButton("Choose color")

        self.color_button.clicked.connect(
            self._color_dialog
        )

        grid.addWidget(color_label, 0, 0)
        grid.addWidget(self.color_button, 0, 1)

        effect_label = QLabel("Backlight effect")

        self.effect_combobox = QComboBox()
        self.effect_combobox.addItems(EFFECTS)

        self.effect_combobox.currentTextChanged.connect(
            self._change_effect
        )

        grid.addWidget(effect_label, 1, 0)
        grid.addWidget(self.effect_combobox, 1, 1)

        profile_label = QLabel("System profile")

        self.profile_combobox = QComboBox()
        self.profile_combobox.addItems(PROFILES)

        self.profile_combobox.currentIndexChanged.connect(
            self._change_profile
        )

        grid.addWidget(profile_label, 2, 0)
        grid.addWidget(self.profile_combobox, 2, 1)

    def _apply_style(self):
        style_path = (
            Path(__file__).resolve().parent
            / "styles"
            / "dark.qss"
        )

        if not style_path.exists():
            return

        try:
            self.setStyleSheet(
                style_path.read_text(encoding="utf-8")
            )
        except OSError as error:
            self._show_error(
                "Style error",
                f"Could not load stylesheet:\n{error}",
            )

    def _run_command(self, arguments, callback=None):
        # Use a separate process for every command
        process = QProcess(self)

        self.processes.add(process)

        process.setProgram("asusctl")
        process.setArguments(arguments)

        def finished(exit_code, exit_status):
            stdout = bytes(
                process.readAllStandardOutput()
            ).decode("utf-8", errors="replace").strip()

            stderr = bytes(
                process.readAllStandardError()
            ).decode("utf-8", errors="replace").strip()

            self.processes.discard(process)
            process.deleteLater()

            if exit_status != QProcess.ExitStatus.NormalExit:
                self._show_error(
                    "asusctl error",
                    "asusctl did not exit normally.",
                )
                return

            if exit_code != 0:
                message = stderr or stdout

                if not message:
                    message = (
                        f"asusctl exited with code {exit_code}."
                    )

                self._show_error(
                    "asusctl command failed",
                    message,
                )
                return

            if callback:
                callback(stdout)

        def error_occurred(error):
            if error == QProcess.ProcessError.FailedToStart:
                self._show_error(
                    "asusctl not found",
                    (
                        "Could not start asusctl.\n\n"
                        "Make sure asusctl is installed and "
                        "available in PATH."
                    ),
                )

        process.finished.connect(finished)
        process.errorOccurred.connect(error_occurred)

        process.start()

    def _change_profile(self, index):
        if index < 0 or index >= len(PROFILES):
            return

        profile = PROFILES[index].lower()

        self._run_command(
            ["profile", "set", profile]
        )

    def _load_current_profile(self):
        self._run_command(
            ["profile", "get"],
            self._parse_current_profile,
        )

    def _parse_current_profile(self, output):
        if not output:
            return

        current_profile = None

        for profile in PROFILES:
            if re.search(
                rf"\b{re.escape(profile)}\b",
                output,
                re.IGNORECASE,
            ):
                current_profile = profile
                break

        if current_profile is None:
            return

        index = PROFILES.index(current_profile)

        # Don't call _change_profile when setting the index
        self.profile_combobox.blockSignals(True)
        self.profile_combobox.setCurrentIndex(index)
        self.profile_combobox.blockSignals(False)

    def _color_dialog(self):
        color = QColorDialog.getColor(
            QColor(self.current_color),
            self,
            "Choose backlight color",
        )

        if not color.isValid():
            return

        self.current_color = color.name().lower()

        # Apply the new color immediately for static effect
        if self.effect_combobox.currentText() == "static":
            self._apply_effect("static")

    def _change_effect(self, effect):
        self._apply_effect(effect)

    def _apply_effect(self, effect):
        color = self.current_color.lstrip("#")
        color2 = self._secondary_color()

        commands = {
            "static": [
                "aura",
                "effect",
                "static",
                "-c",
                color,
            ],

            "breathe": [
                "aura",
                "effect",
                "breathe",
                "--colour",
                color,
                "--colour2",
                color2,
                "--speed",
                SPEED,
            ],

            "rainbow-cycle": [
                "aura",
                "effect",
                "rainbow-cycle",
                "--speed",
                SPEED,
            ],

            "rainbow-wave": [
                "aura",
                "effect",
                "rainbow-wave",
                "--direction",
                RAINBOW_DIRECTION,
                "--speed",
                SPEED,
            ],

            "stars": [
                "aura",
                "effect",
                "stars",
                "--colour",
                color,
                "--colour2",
                color2,
                "--speed",
                SPEED,
            ],

            "rain": [
                "aura",
                "effect",
                "rain",
                "--speed",
                SPEED,
            ],

            "highlight": [
                "aura",
                "effect",
                "highlight",
                "-c",
                color,
                "--speed",
                SPEED,
            ],

            "laser": [
                "aura",
                "effect",
                "laser",
                "-c",
                color,
                "--speed",
                SPEED,
            ],

            "ripple": [
                "aura",
                "effect",
                "ripple",
                "-c",
                color,
                "--speed",
                SPEED,
            ],

            "pulse": [
                "aura",
                "effect",
                "pulse",
                "-c",
                color,
            ],

            "comet": [
                "aura",
                "effect",
                "comet",
                "-c",
                color,
            ],

            "flash": [
                "aura",
                "effect",
                "flash",
                "-c",
                color,
            ],
        }

        arguments = commands.get(effect)

        if arguments is None:
            self._show_error(
                "Unknown effect",
                f"Unsupported effect: {effect}",
            )
            return

        self._run_command(arguments)

    def _secondary_color(self):
        color = QColor(self.current_color)

        red = 255 - color.red()
        green = 255 - color.green()
        blue = 255 - color.blue()

        return f"{red:02x}{green:02x}{blue:02x}"

    def _show_error(self, title, message):
        QMessageBox.critical(
            self,
            title,
            message,
        )


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
