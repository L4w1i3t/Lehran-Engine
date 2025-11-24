"""
Map Editor for Lehran Engine
Handles Tiled integration and map management
"""

import os
import subprocess
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                              QGroupBox, QPushButton, QLabel, QLineEdit,
                              QTextEdit, QFileDialog, QMessageBox, QFormLayout,
                              QSpinBox)
from PyQt6.QtCore import Qt


class MapEditor(QWidget):
    """Editor for map management and Tiled integration"""
    
    def __init__(self):
        super().__init__()
        self.maps = []
        self.tiled_path = ""
        self.project_path = ""
        self.init_ui()
        
    def init_ui(self):
        """Initialize the map editor UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Tiled configuration
        tiled_group = QGroupBox("Tiled Configuration")
        tiled_layout = QHBoxLayout()
        
        tiled_layout.addWidget(QLabel("Tiled Path:"))
        self.tiled_path_input = QLineEdit()
        self.tiled_path_input.setPlaceholderText("Path to Tiled executable")
        tiled_layout.addWidget(self.tiled_path_input)
        
        browse_tiled_btn = QPushButton("Browse...")
        browse_tiled_btn.clicked.connect(self.browse_tiled)
        tiled_layout.addWidget(browse_tiled_btn)
        
        tiled_group.setLayout(tiled_layout)
        layout.addWidget(tiled_group)
        
        # Map management section
        maps_layout = QHBoxLayout()
        
        # Left side - map list
        left_layout = QVBoxLayout()
        
        left_layout.addWidget(QLabel("Maps:"))
        self.map_list = QListWidget()
        self.map_list.currentRowChanged.connect(self.on_map_selected)
        left_layout.addWidget(self.map_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        import_btn = QPushButton("Import Map")
        import_btn.clicked.connect(self.import_map)
        btn_layout.addWidget(import_btn)
        
        new_tiled_btn = QPushButton("New in Tiled")
        new_tiled_btn.clicked.connect(self.create_new_tiled_map)
        btn_layout.addWidget(new_tiled_btn)
        
        edit_btn = QPushButton("Edit in Tiled")
        edit_btn.clicked.connect(self.edit_in_tiled)
        btn_layout.addWidget(edit_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_map)
        btn_layout.addWidget(remove_btn)
        
        left_layout.addLayout(btn_layout)
        
        maps_layout.addLayout(left_layout, 1)
        
        # Right side - map details
        right_layout = QVBoxLayout()
        
        details_group = QGroupBox("Map Details")
        details_layout = QFormLayout()
        
        self.map_name = QLineEdit()
        self.map_file = QLineEdit()
        self.map_file.setReadOnly(True)
        self.map_width = QSpinBox()
        self.map_width.setMaximum(999)
        self.map_width.setReadOnly(True)
        self.map_height = QSpinBox()
        self.map_height.setMaximum(999)
        self.map_height.setReadOnly(True)
        self.map_description = QTextEdit()
        self.map_description.setMaximumHeight(100)
        
        details_layout.addRow("Map Name:", self.map_name)
        details_layout.addRow("File:", self.map_file)
        details_layout.addRow("Width:", self.map_width)
        details_layout.addRow("Height:", self.map_height)
        details_layout.addRow("Description:", self.map_description)
        
        details_group.setLayout(details_layout)
        right_layout.addWidget(details_group)
        
        # Map info
        info_group = QGroupBox("Tiled Integration Info")
        info_layout = QVBoxLayout()
        
        info_text = QLabel(
            "Lehran Engine uses Tiled for map creation.\n\n"
            "Instructions:\n"
            "1. Set the path to your Tiled executable above\n"
            "2. Click 'New in Tiled' to create a new map\n"
            "3. Edit maps in Tiled with standard Fire Emblem tiles\n"
            "4. Import .tmx files back into the engine\n\n"
            "Map Format: Orthogonal, TMX format\n"
            "Tile Size: 16x16 pixels (recommended)"
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        
        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)
        
        right_layout.addStretch()
        maps_layout.addLayout(right_layout, 2)
        
        layout.addLayout(maps_layout)
        
    def browse_tiled(self):
        """Browse for Tiled executable"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Tiled Executable",
            "",
            "Executable Files (*.exe);;All Files (*)"
        )
        if file_path:
            self.tiled_path = file_path
            self.tiled_path_input.setText(file_path)
            
    def import_map(self):
        """Import a TMX map file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Tiled Map",
            "",
            "Tiled Map Files (*.tmx);;All Files (*)"
        )
        
        if file_path:
            map_name = os.path.splitext(os.path.basename(file_path))[0]
            map_data = {
                'name': map_name,
                'file': file_path,
                'width': 0,  # TODO: Parse from TMX
                'height': 0,  # TODO: Parse from TMX
                'description': ''
            }
            self.maps.append(map_data)
            self.map_list.addItem(map_name)
            
    def create_new_tiled_map(self):
        """Create a new map in Tiled"""
        if not self.tiled_path or not os.path.exists(self.tiled_path):
            QMessageBox.warning(
                self,
                "Tiled Not Found",
                "Please set the path to Tiled executable first."
            )
            return
            
        try:
            subprocess.Popen([self.tiled_path])
            QMessageBox.information(
                self,
                "Tiled Launched",
                "Create your map in Tiled and save it to the project's maps folder.\n"
                "Then use 'Import Map' to add it to your project."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch Tiled: {e}")
            
    def edit_in_tiled(self):
        """Edit selected map in Tiled"""
        row = self.map_list.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Please select a map to edit")
            return
            
        if not self.tiled_path or not os.path.exists(self.tiled_path):
            QMessageBox.warning(
                self,
                "Tiled Not Found",
                "Please set the path to Tiled executable first."
            )
            return
            
        map_file = self.maps[row]['file']
        if not os.path.exists(map_file):
            QMessageBox.warning(self, "Warning", "Map file not found")
            return
            
        try:
            subprocess.Popen([self.tiled_path, map_file])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch Tiled: {e}")
            
    def remove_map(self):
        """Remove selected map"""
        row = self.map_list.currentRow()
        if row >= 0:
            self.maps.pop(row)
            self.map_list.takeItem(row)
            
    def on_map_selected(self, index):
        """Handle map selection"""
        if 0 <= index < len(self.maps):
            map_data = self.maps[index]
            self.map_name.setText(map_data['name'])
            self.map_file.setText(map_data['file'])
            self.map_width.setValue(map_data.get('width', 0))
            self.map_height.setValue(map_data.get('height', 0))
            self.map_description.setPlainText(map_data.get('description', ''))
            
    def launch_tiled(self):
        """Launch Tiled editor"""
        if not self.tiled_path or not os.path.exists(self.tiled_path):
            QMessageBox.warning(
                self,
                "Tiled Not Found",
                "Please set the path to Tiled executable in the Maps tab."
            )
            return
            
        try:
            subprocess.Popen([self.tiled_path])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch Tiled: {e}")
            
    def get_data(self):
        """Get maps data"""
        return {
            'map_files': self.maps,
            'tiled_path': self.tiled_path
        }
        
    def load_data(self, data):
        """Load maps data"""
        # Block signals during load to prevent triggering change detection
        self.map_list.blockSignals(True)
        
        try:
            self.maps = data.get('map_files', [])
            self.tiled_path = data.get('tiled_path', '')
            self.tiled_path_input.setText(self.tiled_path)
            
            self.map_list.clear()
            for map_data in self.maps:
                self.map_list.addItem(map_data['name'])
        finally:
            # Always restore signals
            self.map_list.blockSignals(False)
