import sys
import shutil
import os
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QLabel, QLineEdit, QPushButton, QFileDialog
)
from PySide6.QtCore import Qt, QMimeData, QUrl
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import QEvent


# Default destination path for copied files
DEFAULT_DESTINATION_PATH = str(Path.home() / "Downloads")


class DropZoneWidget(QWidget):
    """Custom widget that accepts dropped files"""
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QWidget {
                border: 2px dashed #888;
                border-radius: 8px;
                background-color: #f0f0f0;
            }
            QWidget:hover {
                background-color: #e8e8e8;
            }
        """)
        
        layout = QVBoxLayout()
        self.label = QLabel("Drag file here")
        self.label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setMinimumHeight(100)
        self.dropped_file = None
    
    def dragEnterEvent(self, event):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QWidget {
                    border: 2px dashed #0078d7;
                    border-radius: 8px;
                    background-color: #e3f2fd;
                }
            """)
    
    def dragLeaveEvent(self, event):
        """Handle drag leave event"""
        self.setStyleSheet("""
            QWidget {
                border: 2px dashed #888;
                border-radius: 8px;
                background-color: #f0f0f0;
            }
        """)
    
    def dropEvent(self, event):
        """Handle drop event"""
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            urls = mime_data.urls()
            if urls:
                # Get first file URL
                file_path = urls[0].toLocalFile()
                self.dropped_file = file_path
                filename = Path(file_path).name
                self.label.setText(f"✓ {filename}")
                event.acceptProposedAction()
        
        # Reset styling
        self.setStyleSheet("""
            QWidget {
                border: 2px dashed #888;
                border-radius: 8px;
                background-color: #f0f0f0;
            }
        """)


class FileDropApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.destination_path = DEFAULT_DESTINATION_PATH
        self.initUI()
    
    def initUI(self):
        """Initialize user interface"""
        self.setWindowTitle("Drop to Backup")
        self.setGeometry(100, 100, 300, 250)
        
        # Set window to stay on top
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # Main widget
        main_widget = QWidget()
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # Drop zone
        self.drop_zone = DropZoneWidget()
        layout.addWidget(QLabel("Source File:"))
        layout.addWidget(self.drop_zone)
        
        # Destination path
        layout.addWidget(QLabel("Destination:"))
        self.dest_input = QLineEdit()
        self.dest_input.setText(self.destination_path)
        self.dest_input.setReadOnly(False)
        layout.addWidget(self.dest_input)
        
        # Browse button
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_destination)
        layout.addWidget(browse_btn)
        
        # Copy button
        copy_btn = QPushButton("Copy File")
        copy_btn.clicked.connect(self.copy_file)
        layout.addWidget(copy_btn)
        
        layout.addStretch()
        self.setCentralWidget(main_widget)
    
    def browse_destination(self):
        """Open directory selection dialog"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Destination Directory", self.destination_path
        )
        if directory:
            self.destination_path = directory
            self.dest_input.setText(directory)
    
    def copy_file(self):
        """Copy the dropped file to destination"""
        if not self.drop_zone.dropped_file:
            self.drop_zone.label.setText("⚠ No file selected")
            return
        
        source = self.drop_zone.dropped_file
        destination_dir = self.dest_input.text()
        
        # Validate paths
        if not os.path.exists(source):
            self.drop_zone.label.setText("⚠ Source file not found")
            return
        
        if not os.path.isdir(destination_dir):
            self.drop_zone.label.setText("⚠ Invalid destination")
            return
        
        try:
            # Get filename and create destination path with timestamp prefix
            filename = os.path.basename(source)
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            new_filename = f"{timestamp}_{filename}"
            dest_file = os.path.join(destination_dir, new_filename)
            
            # Copy file
            if os.path.isfile(source):
                shutil.copy2(source, dest_file)
            else:
                shutil.copytree(source, dest_file, dirs_exist_ok=True)
            
            self.drop_zone.label.setText(f"✅ Copied to\n{destination_dir}")
        
        except Exception as e:
            self.drop_zone.label.setText(f"❌ Error: {str(e)[:30]}")


def main():
    app = QApplication(sys.argv)
    window = FileDropApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
