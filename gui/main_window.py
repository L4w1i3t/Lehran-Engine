"""
Main window for Lehran Engine
"""

import os
import logging
import traceback
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QTabWidget, QMenuBar, QMenu, QStatusBar,
                              QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon

logger = logging.getLogger(__name__)

from .story_editor import StoryEditor
from .gameplay_editor import GameplayEditor
from .map_editor import MapEditor
from .timeline_editor import TimelineEditor
from .project_manager import ProjectManager
from .build_manager import BuildDialog, RunGameDialog
from .asset_manager import AssetManager
from .theme_manager import ThemeManager
from .settings_manager import SettingsManager


class MainWindow(QMainWindow):
    """Main application window for Lehran Engine"""
    
    def __init__(self, theme_manager: ThemeManager = None, settings_manager: SettingsManager = None):
        super().__init__()
        logger.info("Initializing MainWindow...")
        
        try:
            # Store theme and settings managers
            self.theme_manager = theme_manager
            self.settings_manager = settings_manager
            
            logger.info("Creating ProjectManager...")
            self.project_manager = ProjectManager()
            self.current_project = None
            self.has_unsaved_changes = False  # Track unsaved changes
            self.is_loading_project = False  # Flag to prevent marking as modified during load
            
            logger.info("Initializing UI components...")
            self.init_ui()
            self.create_menu_bar()
            self.create_status_bar()
            
            # Restore window geometry from settings
            if self.settings_manager:
                geom = self.settings_manager.get_window_geometry()
                self.setGeometry(geom['x'], geom['y'], geom['width'], geom['height'])
            
            logger.info("MainWindow initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing MainWindow: {e}")
            logger.error(traceback.format_exc())
            raise
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Lehran Engine Editor")
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
        # Connect to timeline's scene changed signal
        self.timeline_editor.scene.changed.connect(self._on_editor_changed)
        
        # Story Editor Tab
        self.story_editor = StoryEditor()
        self.tabs.addTab(self.story_editor, "Story")
        # Connect story list changes (access via sub-widgets)
        self.story_editor.chapters_widget.chapter_list.model().rowsInserted.connect(self._on_editor_changed)
        self.story_editor.chapters_widget.chapter_list.model().rowsRemoved.connect(self._on_editor_changed)
        self.story_editor.characters_widget.character_list.model().rowsInserted.connect(self._on_editor_changed)
        self.story_editor.characters_widget.character_list.model().rowsRemoved.connect(self._on_editor_changed)
        self.story_editor.supports_widget.supports_list.model().rowsInserted.connect(self._on_editor_changed)
        self.story_editor.supports_widget.supports_list.model().rowsRemoved.connect(self._on_editor_changed)
        
        # Gameplay Editor Tab (pass story_editor for character linking)
        self.gameplay_editor = GameplayEditor(story_editor=self.story_editor)
        self.tabs.addTab(self.gameplay_editor, "Gameplay")
        # Connect gameplay list changes (access via sub-widgets)
        self.gameplay_editor.classes_widget.class_list.model().rowsInserted.connect(self._on_editor_changed)
        self.gameplay_editor.classes_widget.class_list.model().rowsRemoved.connect(self._on_editor_changed)
        self.gameplay_editor.units_widget.unit_list.model().rowsInserted.connect(self._on_editor_changed)
        self.gameplay_editor.units_widget.unit_list.model().rowsRemoved.connect(self._on_editor_changed)
        self.gameplay_editor.weapons_widget.weapon_list.model().rowsInserted.connect(self._on_editor_changed)
        self.gameplay_editor.weapons_widget.weapon_list.model().rowsRemoved.connect(self._on_editor_changed)
        self.gameplay_editor.items_widget.item_list.model().rowsInserted.connect(self._on_editor_changed)
        self.gameplay_editor.items_widget.item_list.model().rowsRemoved.connect(self._on_editor_changed)
        
        # Map Editor Tab
        self.map_editor = MapEditor()
        self.tabs.addTab(self.map_editor, "Maps")
        # Connect map list changes
        self.map_editor.map_list.model().rowsInserted.connect(self._on_editor_changed)
        self.map_editor.map_list.model().rowsRemoved.connect(self._on_editor_changed)
        
        # Asset Manager Tab
        self.asset_manager = AssetManager()
        self.tabs.addTab(self.asset_manager, "Assets")
        
        # Install event filter to detect any user input (keyboard/mouse) in editors
        self.central_widget.installEventFilter(self)
        
        # Disable tabs until project is loaded
        self.set_tabs_enabled(False)
    
    def eventFilter(self, obj, event):
        """Monitor events to detect when user makes changes"""
        # Mark as modified on keyboard input (typing) or mouse clicks in editors
        if self.current_project and self.tabs.isEnabled():
            from PyQt6.QtCore import QEvent
            from PyQt6.QtCore import Qt
            
            # Detect typing or clicking in editors
            if event.type() == QEvent.Type.KeyPress:
                # Ignore save shortcuts and navigation keys
                if event.key() not in (Qt.Key.Key_Control, Qt.Key.Key_S, Qt.Key.Key_Alt, 
                                       Qt.Key.Key_Shift, Qt.Key.Key_Tab, Qt.Key.Key_F5):
                    self.mark_modified()
            elif event.type() == QEvent.Type.MouseButtonRelease:
                # User clicked something (e.g., adding items, editing)
                self.mark_modified()
                
        return super().eventFilter(obj, event)
    
    def _on_editor_changed(self):
        """Called when any editor content changes"""
        # Don't mark as modified if we're currently loading a project
        if self.current_project and not self.is_loading_project:
            try:
                self.mark_modified()
            except RuntimeError:
                # Object may have been deleted (e.g., during scene reconstruction)
                # This is safe to ignore
                pass
        
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
        
        # View Menu
        view_menu = menubar.addMenu("&View")
        
        theme_menu = view_menu.addMenu("&Theme")
        
        # Theme actions with radio button behavior
        theme_group = QAction("Theme Group", self)  # Hidden action to group themes
        
        light_theme_action = QAction("&Light Mode", self)
        light_theme_action.setCheckable(True)
        light_theme_action.triggered.connect(lambda: self.set_theme("light"))
        theme_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction("&Dark Mode", self)
        dark_theme_action.setCheckable(True)
        dark_theme_action.triggered.connect(lambda: self.set_theme("dark"))
        theme_menu.addAction(dark_theme_action)
        
        system_theme_action = QAction("&System Default", self)
        system_theme_action.setCheckable(True)
        system_theme_action.triggered.connect(lambda: self.set_theme("system"))
        theme_menu.addAction(system_theme_action)
        
        # Store theme actions for later reference
        self.theme_actions = {
            'light': light_theme_action,
            'dark': dark_theme_action,
            'system': system_theme_action
        }
        
        # Set initial theme check based on current setting
        if self.settings_manager:
            current_theme = self.settings_manager.get_theme()
            if current_theme in self.theme_actions:
                self.theme_actions[current_theme].setChecked(True)
        
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
        
        build_menu.addSeparator()
        
        open_tiled_action = QAction("Open Map in &Tiled...", self)
        open_tiled_action.triggered.connect(self.open_tiled)
        build_menu.addAction(open_tiled_action)
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("No project loaded")
        
    def set_tabs_enabled(self, enabled):
        """Enable or disable all editor tabs"""
        self.tabs.setEnabled(enabled)
    
    def mark_modified(self):
        """Mark the project as having unsaved changes"""
        if not self.has_unsaved_changes:
            self.has_unsaved_changes = True
            self.update_window_title()
            logger.debug("Project marked as modified")
    
    def mark_saved(self):
        """Mark the project as saved (no unsaved changes)"""
        if self.has_unsaved_changes:
            self.has_unsaved_changes = False
            self.update_window_title()
    
    def update_window_title(self):
        """Update the window title to reflect project state"""
        base_title = "Lehran Engine Editor"
        if self.current_project:
            project_name = self.current_project.get('name', 'Untitled')
            if self.has_unsaved_changes:
                self.setWindowTitle(f"{base_title} - {project_name}*")
            else:
                self.setWindowTitle(f"{base_title} - {project_name}")
        else:
            self.setWindowTitle(base_title)
        
    def new_project(self):
        """Create a new project"""
        project_data = self.project_manager.create_new_project_dialog(self)
        if project_data:
            self.current_project = project_data
            self.load_project_data(project_data)
            self.set_tabs_enabled(True)
            self.has_unsaved_changes = False  # New project is already saved
            self.update_window_title()
            self.status_bar.showMessage(f"Project: {project_data['name']}")
            
    def open_project(self):
        """Open an existing project"""
        logger.info("Opening project dialog...")
        
        try:
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
                logger.info(f"User selected file: {file_path}")
                logger.info("Loading project data...")
                
                project_data = self.project_manager.load_project(file_path)
                
                if project_data:
                    logger.info(f"Project loaded successfully: {project_data.get('name', 'Unknown')}")
                    logger.info("Setting current project...")
                    self.current_project = project_data
                    
                    logger.info("Loading project data into editors...")
                    self.load_project_data(project_data)
                    
                    logger.info("Enabling tabs...")
                    self.set_tabs_enabled(True)
                    
                    logger.info("Resetting unsaved changes flag...")
                    self.has_unsaved_changes = False  # Freshly loaded project has no changes
                    
                    logger.info("Updating window title and status bar...")
                    self.update_window_title()
                    self.status_bar.showMessage(f"Project: {project_data['name']}")
                    
                    logger.info("Project opened successfully!")
                else:
                    logger.error("Project data is None - load failed")
                    QMessageBox.critical(self, "Error", "Failed to load project file")
            else:
                logger.info("User cancelled project open dialog")
                
        except Exception as e:
            logger.error(f"Error in open_project: {e}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Error", f"Failed to open project:\n\n{e}\n\nCheck crash log for details")
            raise
                
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
            self.mark_saved()  # Clear the unsaved changes flag
            self.status_bar.showMessage(f"Project saved: {self.current_project['name']}", 3000)
        else:
            QMessageBox.critical(self, "Error", "Failed to save project")
            
    def load_project_data(self, project_data):
        """Load project data into all editors"""
        try:
            # Set loading flag to prevent marking as modified during load
            self.is_loading_project = True
            
            logger.info("Loading timeline data...")
            self.timeline_editor.load_data(project_data.get('timeline', []))
            
            logger.info("Loading story data...")
            self.story_editor.load_data(project_data.get('story', {}))
            
            logger.info("Loading gameplay data...")
            self.gameplay_editor.load_data(project_data.get('gameplay', {}))
            
            logger.info("Loading map data...")
            self.map_editor.load_data(project_data.get('maps', {}))
            
            logger.info("Setting asset manager project...")
            self.asset_manager.set_project(project_data)
            
            logger.info("All editors loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading project data into editors: {e}")
            logger.error(traceback.format_exc())
            raise
        finally:
            # Always clear the loading flag
            self.is_loading_project = False
        
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
    
    def set_theme(self, theme: str):
        """Set the application theme
        
        Args:
            theme: One of 'light', 'dark', or 'system'
        """
        if self.theme_manager:
            self.theme_manager.set_theme(theme)
        
        if self.settings_manager:
            self.settings_manager.set_theme(theme)
        
        # Update checkmarks on theme menu items
        for theme_name, action in self.theme_actions.items():
            action.setChecked(theme_name == theme)
        
        # Update all editors to reflect new theme
        self.timeline_editor.update_theme()
        # Add update_theme methods to other editors if needed in the future
        
    def closeEvent(self, event):
        """Handle window close event"""
        # Save window geometry
        if self.settings_manager:
            geom = self.geometry()
            self.settings_manager.set_window_geometry(geom.x(), geom.y(), geom.width(), geom.height())
        
        # Only ask about saving if there's a project with unsaved changes
        if self.current_project and self.has_unsaved_changes:
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
            # No unsaved changes, just close
            event.accept()
