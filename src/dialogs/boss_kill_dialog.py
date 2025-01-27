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
        self.label = QLabel("Did you kill the boss before dying?")
        self.label.setStyleSheet("color: #ffffff; font-size: 14px;")
        layout.addWidget(self.label)
        
        # Buttons
        self.button_layout = QHBoxLayout()
        
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
        self.yes_btn.clicked.connect(self.handle_yes)
        
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
        self.no_btn.clicked.connect(lambda: self.done(0))
        
        self.twin_yes_btn = QPushButton("Yes")
        self.twin_yes_btn.setStyleSheet("""
            QPushButton {
                background-color: #006400;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #008000;
            }
        """)
        self.twin_yes_btn.clicked.connect(lambda: self.done(2))
        
        self.twin_no_btn = QPushButton("No")
        self.twin_no_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b0000;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #a00000;
            }
        """)
        self.twin_no_btn.clicked.connect(lambda: self.done(1))
        
        self.button_layout.addWidget(self.yes_btn)
        self.button_layout.addWidget(self.no_btn)
        layout.addLayout(self.button_layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
        """)
        
    def handle_yes(self):
        # Switch to twin boss question
        self.label.setText("Was it a twin boss?")
        self.button_layout.removeWidget(self.yes_btn)
        self.button_layout.removeWidget(self.no_btn)
        self.yes_btn.hide()
        self.no_btn.hide()
        self.button_layout.addWidget(self.twin_yes_btn)
        self.button_layout.addWidget(self.twin_no_btn)
