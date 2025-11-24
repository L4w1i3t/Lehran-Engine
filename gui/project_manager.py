"""
Project Manager for Lehran Engine
Handles project creation, loading, and saving
"""

import json
import os
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QFileDialog, QMessageBox)


class ProjectManager:
    """Manages Lehran Engine projects"""
    
    def __init__(self):
        self.current_project_path = None
        
    def create_new_project_dialog(self, parent=None):
        """Show dialog to create a new project"""
        dialog = NewProjectDialog(parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            project_data = dialog.get_project_data()
            return self.initialize_project(project_data)
        return None
        
    def initialize_project(self, project_data):
        """Initialize a new project with default structure"""
        # Create project folder inside the selected path
        project_folder = os.path.join(project_data['path'], project_data['name'])
        
        # Don't store absolute path in project file - it will be derived from .lehran file location
        project = {
            'name': project_data['name'],
            'created': datetime.now().isoformat(),
            'modified': datetime.now().isoformat(),
            'version': '0.1',
            'timeline': [],
            'story': {
                'chapters': [],
                'characters': [],
                'dialogues': [],
                'supports': []
            },
            'gameplay': {
                'classes': [],
                'units': [],
                'weapons': [],
                'items': [],
                'stats': {
                    'hp': {'min': 1, 'max': 99},
                    'str': {'min': 0, 'max': 30},
                    'mag': {'min': 0, 'max': 30},
                    'skl': {'min': 0, 'max': 30},
                    'spd': {'min': 0, 'max': 30},
                    'lck': {'min': 0, 'max': 30},
                    'def': {'min': 0, 'max': 30},
                    'res': {'min': 0, 'max': 30}
                }
            },
            'maps': {
                'map_files': [],
                'tiled_path': ''
            }
        }
        
        # Create project directory structure
        try:
            os.makedirs(project_folder, exist_ok=True)
            os.makedirs(os.path.join(project_folder, 'maps'), exist_ok=True)
            
            # Create assets folder with subfolders
            assets_folder = os.path.join(project_folder, 'assets')
            os.makedirs(assets_folder, exist_ok=True)
            os.makedirs(os.path.join(assets_folder, 'bgm'), exist_ok=True)
            os.makedirs(os.path.join(assets_folder, 'sfx'), exist_ok=True)
            os.makedirs(os.path.join(assets_folder, 'portraits'), exist_ok=True)
            os.makedirs(os.path.join(assets_folder, 'sprites'), exist_ok=True)
            os.makedirs(os.path.join(assets_folder, 'backgrounds'), exist_ok=True)
            os.makedirs(os.path.join(assets_folder, 'ui'), exist_ok=True)
            os.makedirs(os.path.join(assets_folder, 'animations'), exist_ok=True)
            
            os.makedirs(os.path.join(project_folder, 'scripts'), exist_ok=True)
            os.makedirs(os.path.join(project_folder, 'data'), exist_ok=True)
            
            # Save initial project file
            project_file = os.path.join(project_folder, f"{project_data['name']}.lehran")
            self.current_project_path = project_file
            
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project, f, indent=4)
            
            # Add path back to the project data for runtime use (not saved to file)
            project['path'] = project_folder
                
            return project
            
        except Exception as e:
            print(f"Error creating project: {e}")
            return None
            
    def load_project(self, file_path):
        """Load a project from a .lehran file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                project = json.load(f)
            
            # Always derive the project path from the .lehran file location (not stored in file)
            actual_project_dir = os.path.dirname(os.path.abspath(file_path))
            project['path'] = actual_project_dir
            
            self.current_project_path = file_path
            print(f"Project loaded from: {actual_project_dir}")
            return project
        except Exception as e:
            print(f"Error loading project: {e}")
            return None
            
    def save_project(self, project_data):
        """Save the current project"""
        if not self.current_project_path:
            return False
            
        try:
            # Create a copy of project data without the runtime 'path' field
            # The path is always derived from the .lehran file location, not stored
            save_data = {k: v for k, v in project_data.items() if k != 'path'}
            
            save_data['modified'] = datetime.now().isoformat()
            
            with open(self.current_project_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving project: {e}")
            return False


class NewProjectDialog(QDialog):
    """Dialog for creating a new project"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Lehran Project")
        self.setModal(True)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Get default projects directory
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        default_projects_dir = os.path.join(script_dir, "Projects")
        
        # Info label
        info_label = QLabel("A folder with the project name will be created in the selected location.")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info_label)
        
        layout.addSpacing(10)
        
        # Project name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Project Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("My Fire Emblem Game (leave blank for 'Unnamed Project')")
        self.name_input.textChanged.connect(self.update_preview)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Project path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Parent Directory:"))
        self.path_input = QLineEdit()
        self.path_input.setText(default_projects_dir)
        self.path_input.textChanged.connect(self.update_preview)
        path_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_path)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)
        
        # Preview label
        layout.addSpacing(10)
        preview_label = QLabel("Project will be created at:")
        layout.addWidget(preview_label)
        self.preview_path = QLabel("")
        self.preview_path.setStyleSheet("font-weight: bold; color: #0066cc;")
        self.preview_path.setWordWrap(True)
        layout.addWidget(self.preview_path)
        
        # Buttons
        button_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(create_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def update_preview(self):
        """Update the preview path label"""
        name = self.name_input.text().strip()
        path = self.path_input.text()
        
        # Use "Unnamed Project" if no name provided
        if not name:
            name = "Unnamed Project"
            
        if path:
            full_path = os.path.join(path, name)
            self.preview_path.setText(full_path)
        else:
            self.preview_path.setText("(Select parent directory)")
        
    def browse_path(self):
        """Browse for project directory"""
        # Use current path input as starting directory, or default to current value
        start_dir = self.path_input.text() if self.path_input.text() else ""
        
        path = QFileDialog.getExistingDirectory(
            self, 
            "Select Parent Directory for Project",
            start_dir,
            QFileDialog.Option.ShowDirsOnly
        )
        if path:
            self.path_input.setText(path)
            
    def get_project_data(self):
        """Get the entered project data"""
        # Use "Unnamed Project" if no name is provided
        project_name = self.name_input.text().strip()
        if not project_name:
            project_name = "Unnamed Project"
            
        return {
            'name': project_name,
            'path': self.path_input.text()
        }
