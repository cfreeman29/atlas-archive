from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel

class BossKillDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Boss Status")
        self.setMinimumWidth(300)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Question label
        label = QLabel("Did you kill the boss before dying?")
        label.setStyleSheet("color: #ffffff; font-size: 14px;")
        layout.addWidget(label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.yes_btn = QPushButton("Yes")
        self.yes_btn.setStyleSheet("""
            QPushButton {
                background-color: #006400;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #008000;
            }
        """)
        self.yes_btn.clicked.connect(lambda: self.done(1))
        
        self.no_btn = QPushButton("No")
        self.no_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b0000;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #a00000;
            }
        """)
        self.no_btn.clicked.connect(lambda: self.done(2))
        
        button_layout.addWidget(self.yes_btn)
        button_layout.addWidget(self.no_btn)
        layout.addLayout(button_layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
        """)
