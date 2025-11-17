"""
Main window for Lehran Engine
"""

import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QTabWidget, QMenuBar, QMenu, QStatusBar, QToolBar,
                              QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon

from .story_editor import StoryEditor
from .gameplay_editor import GameplayEditor
from .map_editor import MapEditor
from .timeline_editor import TimelineEditor
from .project_manager import ProjectManager
from .build_manager import BuildDialog, RunGameDialog
from .asset_manager import AssetManager


class MainWindow(QMainWindow):
    """Main application window for Lehran Engine"""
    
    def __init__(self):
        super().__init__()
        self.project_manager = ProjectManager()
        self.current_project = None
        
        self.init_ui()
        self.create_menu_bar()
        self.create_toolbar()
        self.create_status_bar()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Lehran Engine - Fire Emblem Game Editor")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget with tabs
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)
        
        # Create tab widget for different editors
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Timeline Tab
        self.timeline_editor = TimelineEditor()
        self.tabs.addTab(self.timeline_editor, "Timeline")
        
        # Story Editor Tab
        self.story_editor = StoryEditor()
        self.tabs.addTab(self.story_editor, "Story & Narrative")
        
        # Gameplay Editor Tab
        self.gameplay_editor = GameplayEditor()
        self.tabs.addTab(self.gameplay_editor, "Gameplay & Units")
        
        # Map Editor Tab
        self.map_editor = MapEditor()
        self.tabs.addTab(self.map_editor, "Maps & Tiled")
        
        # Asset Manager Tab
        self.asset_manager = AssetManager()
        self.tabs.addTab(self.asset_manager, "Assets")
        
        # Disable tabs until project is loaded
        self.set_tabs_enabled(False)
        
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        
        new_project_action = QAction("&New Project...", self)
        new_project_action.setShortcut("Ctrl+N")
        new_project_action.triggered.connect(self.new_project)
        file_menu.addAction(new_project_action)
        
        open_project_action = QAction("&Open Project...", self)
        open_project_action.setShortcut("Ctrl+O")
        open_project_action.triggered.connect(self.open_project)
        file_menu.addAction(open_project_action)
        
        file_menu.addSeparator()
        
        save_project_action = QAction("&Save Project", self)
        save_project_action.setShortcut("Ctrl+S")
        save_project_action.triggered.connect(self.save_project)
        file_menu.addAction(save_project_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")
        
        # Tools Menu
        tools_menu = menubar.addMenu("&Tools")
        
        open_tiled_action = QAction("Open in &Tiled...", self)
        open_tiled_action.triggered.connect(self.open_tiled)
        tools_menu.addAction(open_tiled_action)
        
        # Build Menu
        build_menu = menubar.addMenu("&Build")
        
        build_action = QAction("&Build Game", self)
        build_action.setShortcut("Ctrl+B")
        build_action.triggered.connect(self.build_game)
        build_menu.addAction(build_action)
        
        run_action = QAction("&Run Game", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self.run_game)
        build_menu.addAction(run_action)
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """Create the toolbar"""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        new_action = QAction("New Project", self)
        new_action.triggered.connect(self.new_project)
        toolbar.addAction(new_action)
        
        open_action = QAction("Open Project", self)
        open_action.triggered.connect(self.open_project)
        toolbar.addAction(open_action)
        
        save_action = QAction("Save Project", self)
        save_action.triggered.connect(self.save_project)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        build_action = QAction("Build", self)
        build_action.triggered.connect(self.build_game)
        toolbar.addAction(build_action)
        
        run_action = QAction("Run", self)
        run_action.triggered.connect(self.run_game)
        toolbar.addAction(run_action)
        
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("No project loaded")
        
    def set_tabs_enabled(self, enabled):
        """Enable or disable all editor tabs"""
        self.tabs.setEnabled(enabled)
        
    def new_project(self):
        """Create a new project"""
        project_data = self.project_manager.create_new_project_dialog(self)
        if project_data:
            self.current_project = project_data
            self.load_project_data(project_data)
            self.set_tabs_enabled(True)
            self.status_bar.showMessage(f"Project: {project_data['name']}")
            
    def open_project(self):
        """Open an existing project"""
        # Get default projects directory
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        default_projects_dir = os.path.join(script_dir, "Projects")
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Lehran Project",
            default_projects_dir,
            "Lehran Project Files (*.lehran);;All Files (*)"
        )
        
        if file_path:
            project_data = self.project_manager.load_project(file_path)
            if project_data:
                self.current_project = project_data
                self.load_project_data(project_data)
                self.set_tabs_enabled(True)
                self.status_bar.showMessage(f"Project: {project_data['name']}")
            else:
                QMessageBox.critical(self, "Error", "Failed to load project file")
                
    def save_project(self):
        """Save the current project"""
        if not self.current_project:
            QMessageBox.warning(self, "Warning", "No project loaded")
            return
            
        # Gather data from all editors
        self.current_project['timeline'] = self.timeline_editor.get_data()
        self.current_project['story'] = self.story_editor.get_data()
        self.current_project['gameplay'] = self.gameplay_editor.get_data()
        self.current_project['maps'] = self.map_editor.get_data()
        # Audio assignments are already stored in self.current_project by asset_manager
        
        success = self.project_manager.save_project(self.current_project)
        if success:
            self.status_bar.showMessage(f"Project saved: {self.current_project['name']}", 3000)
        else:
            QMessageBox.critical(self, "Error", "Failed to save project")
            
    def load_project_data(self, project_data):
        """Load project data into all editors"""
        self.timeline_editor.load_data(project_data.get('timeline', []))
        self.story_editor.load_data(project_data.get('story', {}))
        self.gameplay_editor.load_data(project_data.get('gameplay', {}))
        self.map_editor.load_data(project_data.get('maps', {}))
        self.asset_manager.set_project(project_data)
        
    def open_tiled(self):
        """Open Tiled map editor"""
        if not self.current_project:
            QMessageBox.warning(self, "Warning", "Please create or open a project first")
            return
            
        self.map_editor.launch_tiled()
        
    def build_game(self):
        """Build the game"""
        if not self.current_project:
            QMessageBox.warning(self, "Warning", "No project loaded")
            return
        
        # Save project before building
        self.save_project()
        
        # Show build dialog
        dialog = BuildDialog(self.current_project, self)
        dialog.exec()
        
    def run_game(self):
        """Run the game"""
        if not self.current_project:
            QMessageBox.warning(self, "Warning", "No project loaded")
            return
        
        # Save project before running
        self.save_project()
        
        # Show run dialog
        dialog = RunGameDialog(self.current_project, self)
        dialog.exec()
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Lehran Engine",
            "Lehran Engine v0.1\n\n"
            "A custom Fire Emblem game creation engine.\n\n"
            "Features:\n"
            "- Timeline Editor for Event Organization\n"
            "- Story & Narrative Editor\n"
            "- Gameplay & Units Configuration\n"
            "- Tiled Map Integration\n"
            "- C++ Game Runtime (Coming Soon)\n"
        )
        
    def closeEvent(self, event):
        """Handle window close event"""
        if self.current_project:
            reply = QMessageBox.question(
                self,
                "Quit",
                "Do you want to save changes before quitting?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_project()
                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
