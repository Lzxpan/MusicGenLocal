import sys

from PySide6.QtWidgets import QApplication

from app.core.runtime_paths import ensure_app_directories
from app.ui.main_window import MainWindow
from app.ui.styles import build_stylesheet


def main() -> int:
    directories = ensure_app_directories()
    app = QApplication(sys.argv)
    app.setApplicationName("MusicGenLocal 音樂工作站 V0.91b")
    app.setStyleSheet(build_stylesheet())
    window = MainWindow(repo_root=directories["app_root"])
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
