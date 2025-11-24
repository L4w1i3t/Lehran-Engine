"""
Asset Manager for Lehran Engine
Browse, preview, and manage game assets
"""

import os
import shutil
import logging
import traceback

# Try to import pygame for audio preview (optional)
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: pygame not available - audio preview will be disabled")

logger = logging.getLogger(__name__)

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                              QTreeWidget, QTreeWidgetItem, QLabel, QPushButton,
                              QFileDialog, QGroupBox, QTextEdit, QMessageBox,
                              QComboBox, QScrollArea, QFormLayout, QTabWidget)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QPixmap, QDesktopServices


class AssetManager(QWidget):
    """Widget for managing game assets"""
    
    def __init__(self, project_data=None):
        super().__init__()
        self.project_data = project_data
        self.current_asset_path = None
        self.audio_assignments = {}  # Maps roles to audio file paths
        self.audio_available = False
        self.audio_initialized = False
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the asset manager UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create sub-tabs for Assets
        self.asset_tabs = QTabWidget()
        layout.addWidget(self.asset_tabs)
        
        # Tab 1: Asset Browser
        self.create_asset_browser_tab()
        
        # Tab 2: Audio Assignments
        self.create_audio_assignments_tab()
        
        # Load assets if project is set
        if self.project_data:
            self.refresh_assets()
    
    def create_asset_browser_tab(self):
        """Create the asset browser tab"""
        browser_widget = QWidget()
        layout = QVBoxLayout()
        browser_widget.setLayout(layout)
        
        # Header with instructions
        header = QGroupBox("Asset Browser")
        header.setMaximumHeight(120)
        header_layout = QVBoxLayout()
        
        instructions = QLabel(
            "Browse and manage your game assets. Assets are organized by type.\n"
            "• Right-click folders to add new assets\n"
            "• Click on assets to preview them\n"
            "• Supported formats: Images (PNG, JPG), Audio (OGG, WAV, MP3)"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; padding: 5px;")
        header_layout.addWidget(instructions)
        header.setLayout(header_layout)
        layout.addWidget(header)
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Asset tree
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        
        left_layout.addWidget(QLabel("Asset Folders:"))
        
        self.asset_tree = QTreeWidget()
        self.asset_tree.setHeaderLabel("Assets")
        self.asset_tree.itemClicked.connect(self.on_asset_selected)
        self.asset_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.asset_tree.customContextMenuRequested.connect(self.show_context_menu)
        left_layout.addWidget(self.asset_tree)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Asset List")
        refresh_btn.clicked.connect(self.refresh_assets)
        left_layout.addWidget(refresh_btn)
        
        splitter.addWidget(left_widget)
        
        # Right side - Asset preview
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        
        right_layout.addWidget(QLabel("Asset Preview:"))
        
        # Asset info group
        info_group = QGroupBox("Asset Information")
        info_layout = QVBoxLayout()
        
        self.asset_name_label = QLabel("No asset selected")
        self.asset_name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(self.asset_name_label)
        
        self.asset_info_label = QLabel("")
        self.asset_info_label.setWordWrap(True)
        info_layout.addWidget(self.asset_info_label)
        
        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)
        
        # Preview area
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel("Select an asset to preview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(300, 300)
        self.preview_label.setStyleSheet("background-color: #2b2b2b; color: #888; border: 1px solid #555;")
        preview_layout.addWidget(self.preview_label)
        
        # Audio controls
        self.audio_controls = QWidget()
        audio_controls_layout = QHBoxLayout()
        self.audio_controls.setLayout(audio_controls_layout)
        
        self.play_btn = QPushButton("▶ Play")
        self.play_btn.clicked.connect(self.play_audio)
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.clicked.connect(self.stop_audio)
        
        audio_controls_layout.addWidget(self.play_btn)
        audio_controls_layout.addWidget(self.stop_btn)
        audio_controls_layout.addStretch()
        
        self.audio_controls.hide()
        preview_layout.addWidget(self.audio_controls)
        
        preview_group.setLayout(preview_layout)
        right_layout.addWidget(preview_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.open_folder_btn = QPushButton("Open in File Explorer")
        self.open_folder_btn.clicked.connect(self.open_in_explorer)
        self.open_folder_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("Delete Asset")
        self.delete_btn.clicked.connect(self.delete_asset)
        self.delete_btn.setEnabled(False)
        self.delete_btn.setStyleSheet("color: #ff6666;")
        
        action_layout.addWidget(self.open_folder_btn)
        action_layout.addStretch()
        action_layout.addWidget(self.delete_btn)
        
        right_layout.addLayout(action_layout)
        right_layout.addStretch()
        
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        
        # Add browser widget to tabs
        self.asset_tabs.addTab(browser_widget, "Asset Browser")
    
    def create_audio_assignments_tab(self):
        """Create the audio assignments tab"""
        assignments_widget = QWidget()
        layout = QVBoxLayout()
        assignments_widget.setLayout(layout)
        
        # Header
        header = QGroupBox("Audio Assignments")
        header_layout = QVBoxLayout()
        
        instructions = QLabel(
            "Assign audio files to specific game events and locations.\n\n"
            "Music roles include: Title Screen, Battle Music, Victory/Defeat themes, etc.\n"
            "Sound effect roles include: Menu sounds, Attack sounds, Level Up, etc.\n\n"
            "1. Add audio files to the bgm/sfx folders in the Asset Browser tab\n"
            "2. Click 'Refresh Audio List' below to load available files\n"
            "3. Select the appropriate audio file for each role\n"
            "4. Click 'Save Audio Assignments' when done\n"
            "5. Save your project (Ctrl+S) to persist changes"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; padding: 5px;")
        header_layout.addWidget(instructions)
        header.setLayout(header_layout)
        layout.addWidget(header)
        
        # Scrollable form for audio assignments
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        form_widget = QWidget()
        form_layout = QFormLayout()
        form_widget.setLayout(form_layout)
        
        # Define audio roles/events
        self.audio_roles = [
            ('title_music', 'Title Screen Music'),
            ('main_menu_music', 'Main Menu Music'),
            ('battle_prep_music', 'Battle Prep Music'),
            ('player_phase_music', 'Player Phase Music'),
            ('enemy_phase_music', 'Enemy Phase Music'),
            ('battle_music', 'Battle Scene Music'),
            ('victory_music', 'Victory Music'),
            ('defeat_music', 'Game Over Music'),
            ('shop_music', 'Shop/Base Music'),
            ('cutscene_music', 'Cutscene Music'),
            ('menu_cursor_sfx', 'Menu Cursor SFX'),
            ('menu_select_sfx', 'Menu Select SFX'),
            ('menu_cancel_sfx', 'Menu Cancel SFX'),
            ('attack_hit_sfx', 'Attack Hit SFX'),
            ('attack_miss_sfx', 'Attack Miss SFX'),
            ('critical_hit_sfx', 'Critical Hit SFX'),
            ('level_up_sfx', 'Level Up SFX'),
        ]
        
        self.audio_combo_boxes = {}
        
        for role_id, role_name in self.audio_roles:
            combo = QComboBox()
            combo.addItem("(None)")
            combo.currentTextChanged.connect(lambda text, r=role_id: self.on_audio_assignment_changed(r, text))
            self.audio_combo_boxes[role_id] = combo
            form_layout.addRow(role_name + ":", combo)
        
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)
        
        # Buttons to refresh and apply
        button_layout = QHBoxLayout()
        
        refresh_audio_btn = QPushButton("Refresh Audio List")
        refresh_audio_btn.clicked.connect(self.populate_audio_dropdowns)
        button_layout.addWidget(refresh_audio_btn)
        
        button_layout.addStretch()
        
        save_audio_btn = QPushButton("Save Audio Assignments")
        save_audio_btn.clicked.connect(self.save_audio_assignments)
        save_audio_btn.setStyleSheet("background-color: #2a5a2a; padding: 5px;")
        button_layout.addWidget(save_audio_btn)
        
        layout.addLayout(button_layout)
        
        # Add assignments widget to tabs
        self.asset_tabs.addTab(assignments_widget, "Audio Assignments")
    
    def populate_audio_dropdowns(self):
        """Populate audio dropdowns with available audio files"""
        if not self.project_data:
            return
        
        # Get all audio files from bgm and sfx folders
        audio_files = ['(None)']
        
        assets_path = os.path.join(self.project_data['path'], 'assets')
        
        # Check BGM folder
        bgm_path = os.path.join(assets_path, 'bgm')
        if os.path.exists(bgm_path):
            for filename in sorted(os.listdir(bgm_path)):
                if os.path.isfile(os.path.join(bgm_path, filename)):
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in ['.ogg', '.wav', '.mp3']:
                        audio_files.append(f"bgm/{filename}")
        
        # Check SFX folder
        sfx_path = os.path.join(assets_path, 'sfx')
        if os.path.exists(sfx_path):
            for filename in sorted(os.listdir(sfx_path)):
                if os.path.isfile(os.path.join(sfx_path, filename)):
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in ['.ogg', '.wav', '.mp3']:
                        audio_files.append(f"sfx/{filename}")
        
        # Update all combo boxes
        for role_id, combo in self.audio_combo_boxes.items():
            current_value = combo.currentText()
            combo.clear()
            combo.addItems(audio_files)
            
            # Restore previous selection if it still exists
            if current_value in audio_files:
                combo.setCurrentText(current_value)
            elif role_id in self.audio_assignments and self.audio_assignments[role_id] in audio_files:
                combo.setCurrentText(self.audio_assignments[role_id])
    
    def on_audio_assignment_changed(self, role_id, filename):
        """Handle audio assignment change"""
        if filename == "(None)":
            # Save empty string to explicitly mark as "no music"
            self.audio_assignments[role_id] = ""
        else:
            self.audio_assignments[role_id] = filename
    
    def save_audio_assignments(self):
        """Save audio assignments to project data"""
        if not self.project_data:
            QMessageBox.warning(self, "No Project", "No project is currently loaded.")
            return
        
        # Update project data
        if 'audio_assignments' not in self.project_data:
            self.project_data['audio_assignments'] = {}
        
        self.project_data['audio_assignments'] = self.audio_assignments.copy()
        
        QMessageBox.information(
            self,
            "Saved",
            "Audio assignments saved! Remember to save the project to persist these changes."
        )
    
    def load_audio_assignments(self):
        """Load audio assignments from project data"""
        if not self.project_data:
            return
        
        self.audio_assignments = self.project_data.get('audio_assignments', {}).copy()
        
        # Update combo boxes to reflect loaded assignments
        for role_id, filename in self.audio_assignments.items():
            if role_id in self.audio_combo_boxes:
                combo = self.audio_combo_boxes[role_id]
                index = combo.findText(filename)
                if index >= 0:
                    combo.setCurrentIndex(index)
    
    def set_project(self, project_data):
        """Set the current project"""
        try:
            logger.info("AssetManager: Setting project...")
            self.project_data = project_data
            
            logger.info("AssetManager: Refreshing assets...")
            self.refresh_assets()
            
            logger.info("AssetManager: Populating audio dropdowns...")
            self.populate_audio_dropdowns()
            
            logger.info("AssetManager: Loading audio assignments...")
            self.load_audio_assignments()
            
            logger.info("AssetManager: Project set successfully")
        except Exception as e:
            logger.error(f"AssetManager: Error setting project: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def refresh_assets(self):
        """Refresh the asset tree"""
        try:
            logger.info("AssetManager: Clearing asset tree...")
            self.asset_tree.clear()
            
            if not self.project_data:
                logger.info("AssetManager: No project data, skipping refresh")
                return
            
            assets_path = os.path.join(self.project_data['path'], 'assets')
            logger.info(f"AssetManager: Assets path: {assets_path}")
            
            if not os.path.exists(assets_path):
                logger.info(f"AssetManager: Creating assets directory...")
                os.makedirs(assets_path, exist_ok=True)
            
            # Asset categories
            categories = [
                ('bgm', 'Background Music'),
                ('sfx', 'Sound Effects'),
                ('portraits', 'Character Portraits'),
                ('sprites', 'Unit Sprites'),
                ('backgrounds', 'Backgrounds'),
                ('ui', 'UI Elements'),
                ('animations', 'Animations')
            ]
            
            for folder_name, display_name in categories:
                folder_path = os.path.join(assets_path, folder_name)
                
                # Create folder if it doesn't exist
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path, exist_ok=True)
                
                # Create tree item
                folder_item = QTreeWidgetItem(self.asset_tree, [display_name])
                folder_item.setData(0, Qt.ItemDataRole.UserRole, folder_path)
                
                # Add files in this folder
                try:
                    logger.info(f"AssetManager: Reading folder {folder_name}...")
                    files = os.listdir(folder_path)
                    logger.info(f"AssetManager: Found {len(files)} items in {folder_name}")
                    
                    for filename in sorted(files):
                        file_path = os.path.join(folder_path, filename)
                        if os.path.isfile(file_path):
                            file_item = QTreeWidgetItem(folder_item, [filename])
                            file_item.setData(0, Qt.ItemDataRole.UserRole, file_path)
                            
                            # Add icon/indicator based on file type
                            ext = os.path.splitext(filename)[1].lower()
                            if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
                                file_item.setText(0, f"🖼️ {filename}")
                            elif ext in ['.ogg', '.wav', '.mp3']:
                                file_item.setText(0, f"🎵 {filename}")
                            
                except Exception as e:
                    logger.error(f"AssetManager: Error reading folder {folder_path}: {e}")
                    logger.error(traceback.format_exc())
            
            logger.info("AssetManager: Expanding asset tree...")
            self.asset_tree.expandAll()
            logger.info("AssetManager: Asset tree refresh complete")
            
        except Exception as e:
            logger.error(f"AssetManager: Error in refresh_assets: {e}")
            logger.error(traceback.format_exc())
            raise
    
    def on_asset_selected(self, item, column):
        """Handle asset selection"""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        
        if not file_path or not os.path.isfile(file_path):
            # Folder selected
            self.current_asset_path = None
            self.preview_label.setText("Select a file to preview")
            self.preview_label.setPixmap(QPixmap())
            self.asset_name_label.setText("Folder")
            self.asset_info_label.setText("")
            self.audio_controls.hide()
            self.open_folder_btn.setEnabled(True)
            self.delete_btn.setEnabled(False)
            return
        
        self.current_asset_path = file_path
        self.open_folder_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        
        # Stop any playing audio
        self.stop_audio()
        
        # Get file info
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_ext = os.path.splitext(filename)[1].lower()
        
        size_str = self.format_file_size(file_size)
        
        self.asset_name_label.setText(filename)
        self.asset_info_label.setText(f"Size: {size_str}\nType: {file_ext[1:].upper()}")
        
        # Preview based on file type
        if file_ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
            self.preview_image(file_path)
            self.audio_controls.hide()
        elif file_ext in ['.ogg', '.wav', '.mp3']:
            self.preview_audio(file_path)
            self.audio_controls.show()
        else:
            self.preview_label.setText(f"No preview available for {file_ext} files")
            self.preview_label.setPixmap(QPixmap())
            self.audio_controls.hide()
    
    def preview_image(self, file_path):
        """Preview an image file"""
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            # Scale to fit preview area while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.preview_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)
        else:
            self.preview_label.setText("Failed to load image")
            self.preview_label.setPixmap(QPixmap())
    
    def init_audio(self):
        """Initialize pygame audio (lazy initialization)"""
        if self.audio_initialized:
            return self.audio_available
        
        self.audio_initialized = True
        
        if not PYGAME_AVAILABLE:
            print("Pygame not available - audio preview disabled")
            self.audio_available = False
            return False
        
        try:
            # Try to initialize pygame audio with conservative settings
            pygame.mixer.quit()  # Make sure mixer is stopped first
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=2048)
            self.audio_available = True
            print("Audio initialized successfully")
        except Exception as e:
            print(f"Failed to initialize audio: {e}")
            print("Audio preview will be disabled")
            self.audio_available = False
        
        return self.audio_available
    
    def preview_audio(self, file_path):
        """Preview an audio file"""
        self.preview_label.setText(f"🎵 Audio File\n\n{os.path.basename(file_path)}\n\nClick Play to listen")
        self.preview_label.setPixmap(QPixmap())
    
    def play_audio(self):
        """Play the selected audio file"""
        if not self.current_asset_path:
            return
        
        # Initialize audio if not already done
        if not self.audio_initialized:
            if not self.init_audio():
                QMessageBox.warning(
                    self,
                    "Audio Not Available",
                    "Audio playback is not available on this system.\n\n"
                    "This may be due to missing audio drivers or codecs.\n"
                    "The editor will work normally, but audio preview is disabled."
                )
                return
        
        if not self.audio_available:
            return
        
        try:
            pygame.mixer.music.load(self.current_asset_path)
            pygame.mixer.music.play()
            pygame.mixer.music.set_volume(0.5)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Audio Error",
                f"Failed to play audio file:\n{str(e)}\n\n"
                "The file may be corrupted or in an unsupported format."
            )
    
    def stop_audio(self):
        """Stop audio playback"""
        if self.audio_available and self.audio_initialized:
            try:
                pygame.mixer.music.stop()
            except Exception as e:
                # Silently ignore errors when stopping audio
                print(f"Error stopping audio: {e}")
                pass
    
    def open_in_explorer(self):
        """Open the asset's folder in file explorer"""
        if self.current_asset_path:
            folder = os.path.dirname(self.current_asset_path)
        else:
            # Get selected folder
            item = self.asset_tree.currentItem()
            if item:
                folder = item.data(0, Qt.ItemDataRole.UserRole)
            else:
                return
        
        if folder and os.path.exists(folder):
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder))
    
    def delete_asset(self):
        """Delete the selected asset"""
        if not self.current_asset_path:
            return
        
        filename = os.path.basename(self.current_asset_path)
        reply = QMessageBox.question(
            self,
            "Delete Asset",
            f"Are you sure you want to delete '{filename}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(self.current_asset_path)
                self.refresh_assets()
                self.current_asset_path = None
                self.preview_label.setText("Asset deleted")
                self.preview_label.setPixmap(QPixmap())
                self.asset_name_label.setText("No asset selected")
                self.asset_info_label.setText("")
                self.open_folder_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete asset:\n{str(e)}")
    
    def show_context_menu(self, position):
        """Show context menu for adding assets"""
        item = self.asset_tree.itemAt(position)
        if not item:
            return
        
        # Get the folder path (either the item itself or its parent)
        folder_path = item.data(0, Qt.ItemDataRole.UserRole)
        if not folder_path or os.path.isfile(folder_path):
            # If it's a file, get the parent folder
            if item.parent():
                folder_path = item.parent().data(0, Qt.ItemDataRole.UserRole)
        
        if not folder_path or not os.path.isdir(folder_path):
            return
        
        # Create context menu
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        
        add_action = menu.addAction("Add Asset to this folder...")
        action = menu.exec(self.asset_tree.viewport().mapToGlobal(position))
        
        if action == add_action:
            self.add_asset_to_folder(folder_path)
    
    def add_asset_to_folder(self, folder_path):
        """Add a new asset to the specified folder"""
        # Determine file filter based on folder
        folder_name = os.path.basename(folder_path)
        
        if folder_name in ['bgm', 'sfx']:
            file_filter = "Audio Files (*.ogg *.wav *.mp3);;All Files (*.*)"
        elif folder_name in ['portraits', 'sprites', 'backgrounds', 'ui', 'animations']:
            file_filter = "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*.*)"
        else:
            file_filter = "All Files (*.*)"
        
        # Open file dialog
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Assets to Add",
            "",
            file_filter
        )
        
        if files:
            for file_path in files:
                try:
                    filename = os.path.basename(file_path)
                    dest_path = os.path.join(folder_path, filename)
                    
                    # Check if file already exists
                    if os.path.exists(dest_path):
                        reply = QMessageBox.question(
                            self,
                            "File Exists",
                            f"'{filename}' already exists. Overwrite?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.No
                        )
                        if reply != QMessageBox.StandardButton.Yes:
                            continue
                    
                    # Copy file
                    shutil.copy2(file_path, dest_path)
                    
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to add {filename}:\n{str(e)}")
            
            # Refresh the asset tree
            self.refresh_assets()
            QMessageBox.information(self, "Success", f"Added {len(files)} asset(s)")
    
    def format_file_size(self, size_bytes):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def get_data(self):
        """Get asset data (not needed for assets, but kept for consistency)"""
        return {}
    
    def load_data(self, data):
        """Load asset data (refresh the view)"""
        self.refresh_assets()
