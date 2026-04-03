def build_stylesheet() -> str:
    return """
    QWidget {
        background: #f4f6fb;
        color: #172033;
        font-family: "Segoe UI";
        font-size: 10pt;
    }
    QMainWindow, QScrollArea, QFrame[card="true"] {
        background: transparent;
    }
    QLabel[title="true"] {
        font-size: 20pt;
        font-weight: 700;
        color: #0f172a;
    }
    QLabel[section="true"] {
        font-size: 11pt;
        font-weight: 700;
        color: #24324d;
        margin-top: 8px;
    }
    QFrame[card="true"] {
        background: #ffffff;
        border: 1px solid #d9e0ee;
        border-radius: 18px;
    }
    QPushButton {
        background: #e9eef8;
        border: 1px solid #d4dbea;
        border-radius: 10px;
        padding: 8px 12px;
        font-weight: 600;
    }
    QPushButton:hover {
        background: #dde7fb;
    }
    QPushButton[primary="true"] {
        background: #1d4ed8;
        color: white;
        border: 1px solid #1d4ed8;
    }
    QPushButton[primary="true"]:hover {
        background: #1b46c4;
    }
    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QListWidget, QSpinBox, QTableWidget {
        background: #fbfcff;
        border: 1px solid #d7dfef;
        border-radius: 10px;
        padding: 6px;
        selection-background-color: #cfe0ff;
    }
    QHeaderView::section {
        background: #eef3fb;
        color: #32415f;
        padding: 8px;
        border: none;
        border-bottom: 1px solid #d7dfef;
        font-weight: 600;
    }
    QProgressBar {
        border: 1px solid #d7dfef;
        border-radius: 8px;
        background: #edf2fb;
        text-align: center;
        min-height: 18px;
    }
    QProgressBar::chunk {
        border-radius: 8px;
        background: #1d4ed8;
    }
    QListWidget::item {
        padding: 4px 2px;
    }
    """
