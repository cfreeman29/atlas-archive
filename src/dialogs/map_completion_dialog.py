from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel

class MapCompletionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Map Completion Status")
        self.setMinimumWidth(300)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Status label
        label = QLabel("How did the map end?")
        label.setStyleSheet("color: #ffffff; font-size: 14px;")
        layout.addWidget(label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.complete_btn = QPushButton("Complete")
        self.complete_btn.setStyleSheet("""
            QPushButton {
                background-color: #006400;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #008000;
            }
        """)
        self.complete_btn.clicked.connect(lambda: self.done(1))
        
        self.rip_btn = QPushButton("RIP")
        self.rip_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b0000;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #a00000;
            }
        """)
        self.rip_btn.clicked.connect(lambda: self.done(2))
        
        button_layout.addWidget(self.complete_btn)
        button_layout.addWidget(self.rip_btn)
        layout.addLayout(button_layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
        """)
