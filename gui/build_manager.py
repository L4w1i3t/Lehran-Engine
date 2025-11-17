"""
Build Manager for Lehran Engine
Handles building and running game projects
"""

import os
import json
import shutil
import subprocess
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTextEdit, QProgressBar, QCheckBox,
                              QGroupBox, QRadioButton, QButtonGroup)
from PyQt6.QtCore import QThread, pyqtSignal, Qt


class BuildThread(QThread):
    """Thread for building the project"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, project_data, build_options):
        super().__init__()
        self.project_data = project_data
        self.build_options = build_options
        
    def run(self):
        """Build the project"""
        try:
            project_path = self.project_data['path']
            build_path = os.path.join(project_path, 'build')
            
            # Step 1: Create build directory
            self.progress.emit(10, "Creating build directory...")
            os.makedirs(build_path, exist_ok=True)
            
            # Step 2: Copy assets
            self.progress.emit(20, "Copying assets...")
            assets_src = os.path.join(project_path, 'assets')
            assets_dst = os.path.join(build_path, 'assets')
            if os.path.exists(assets_src):
                shutil.copytree(assets_src, assets_dst, dirs_exist_ok=True)
            
            # Step 3: Copy maps
            self.progress.emit(25, "Copying maps...")
            maps_src = os.path.join(project_path, 'maps')
            maps_dst = os.path.join(build_path, 'maps')
            if os.path.exists(maps_src):
                shutil.copytree(maps_src, maps_dst, dirs_exist_ok=True)
            
            # Step 4: Export game data
            self.progress.emit(30, "Exporting game data...")
            data_dst = os.path.join(build_path, 'data')
            os.makedirs(data_dst, exist_ok=True)
            
            # Export story data
            story_file = os.path.join(data_dst, 'story.json')
            with open(story_file, 'w', encoding='utf-8') as f:
                json.dump(self.project_data['story'], f, indent=2)
            
            # Export gameplay data
            gameplay_file = os.path.join(data_dst, 'gameplay.json')
            with open(gameplay_file, 'w', encoding='utf-8') as f:
                json.dump(self.project_data['gameplay'], f, indent=2)
            
            # Export timeline
            timeline_file = os.path.join(data_dst, 'timeline.json')
            with open(timeline_file, 'w', encoding='utf-8') as f:
                json.dump(self.project_data['timeline'], f, indent=2)
            
            # Export audio assignments
            audio_assignments = self.project_data.get('audio_assignments', {})
            audio_file = os.path.join(data_dst, 'audio_assignments.json')
            with open(audio_file, 'w', encoding='utf-8') as f:
                json.dump(audio_assignments, f, indent=2)
            
            # Step 5: Create game manifest
            self.progress.emit(35, "Creating game manifest...")
            manifest = {
                'name': self.project_data['name'],
                'version': self.project_data['version'],
                'built': datetime.now().isoformat(),
                'engine_version': '0.1',
                'debug_mode': self.build_options.get('debug_mode', False)
            }
            
            manifest_file = os.path.join(build_path, 'manifest.json')
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            
            # Also copy manifest to data folder for engine to find
            data_manifest = os.path.join(data_dst, 'manifest.json')
            shutil.copy2(manifest_file, data_manifest)
            
            # Step 6: Copy C++ game engine runtime
            self.progress.emit(40, "Copying game engine runtime...")
            runtime_src = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'runtime')
            
            # Copy engine executable
            engine_exe_src = os.path.join(runtime_src, 'LehranEngine.exe')
            engine_exe_dst = os.path.join(build_path, f"{self.project_data['name']}.exe")
            if os.path.exists(engine_exe_src):
                shutil.copy2(engine_exe_src, engine_exe_dst)
            else:
                raise Exception("Engine runtime not found. Please build the C++ engine first.")
            
            # Copy SDL2 DLLs
            self.progress.emit(50, "Copying required DLLs...")
            dll_files = [
                'SDL2.dll', 
                'SDL2_ttf.dll',
                'SDL2_mixer.dll',
                'vorbis.dll',
                'vorbisfile.dll',
                'ogg.dll',
                'wavpackdll.dll'
            ]
            for dll in dll_files:
                dll_src = os.path.join(runtime_src, dll)
                dll_dst = os.path.join(build_path, dll)
                if os.path.exists(dll_src):
                    shutil.copy2(dll_src, dll_dst)
                else:
                    # Non-critical DLLs (audio dependencies) - warn but don't fail
                    if dll not in ['SDL2.dll', 'SDL2_ttf.dll']:
                        self.progress.emit(50, f"Warning: {dll} not found (audio may not work)")
                    else:
                        raise Exception(f"Required DLL not found: {dll}")
            
            # Step 7: Create README
            self.progress.emit(95, "Creating documentation...")
            readme_file = os.path.join(build_path, 'README.txt')
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(f"Lehran Engine Build\n")
                f.write(f"===================\n\n")
                f.write(f"Project: {self.project_data['name']}\n")
                f.write(f"Built: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Engine Version: 0.1\n\n")
                f.write(f"To run the game, double-click: {self.project_data['name']}.exe\n\n")
                f.write("Build contents:\n")
                f.write(f"- {self.project_data['name']}.exe : Game executable (C++ Lehran Engine)\n")
                f.write("- SDL2.dll, SDL2_ttf.dll : Required libraries\n")
                f.write("- SDL2_mixer.dll, vorbis.dll, etc. : Audio libraries\n")
                f.write("- data/           : Game data (story, gameplay, timeline)\n")
                f.write("- assets/         : Game resources (BGM, SFX, portraits, etc.)\n")
                f.write("- maps/           : Level maps (if any)\n")
                f.write("- manifest.json   : Build information\n")
            
            # Step 8: Complete
            self.progress.emit(100, "Build complete!")
            self.finished.emit(True, f"Build created successfully!\n\nExecutable: {build_path}\\{self.project_data['name']}.exe\nBuild folder: {build_path}")
            
        except Exception as e:
            self.finished.emit(False, f"Build failed: {str(e)}")
            self.finished.emit(False, f"Build failed: {str(e)}")


class BuildDialog(QDialog):
    """Dialog for building the project"""
    
    def __init__(self, project_data, parent=None):
        super().__init__(parent)
        self.project_data = project_data
        self.build_thread = None
        self.setWindowTitle(f"Build Project - {project_data['name']}")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Build options
        options_group = QGroupBox("Build Options")
        options_layout = QVBoxLayout()
        
        self.debug_check = QCheckBox("Include debug information")
        self.debug_check.setChecked(True)
        options_layout.addWidget(self.debug_check)
        
        self.optimize_check = QCheckBox("Optimize assets (placeholder)")
        self.optimize_check.setEnabled(False)
        options_layout.addWidget(self.optimize_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Platform selection (placeholder)
        platform_group = QGroupBox("Target Platform (placeholder)")
        platform_layout = QVBoxLayout()
        
        self.platform_buttons = QButtonGroup()
        windows_radio = QRadioButton("Windows")
        windows_radio.setChecked(True)
        mac_radio = QRadioButton("macOS")
        mac_radio.setEnabled(False)
        linux_radio = QRadioButton("Linux")
        linux_radio.setEnabled(False)
        
        self.platform_buttons.addButton(windows_radio, 0)
        self.platform_buttons.addButton(mac_radio, 1)
        self.platform_buttons.addButton(linux_radio, 2)
        
        platform_layout.addWidget(windows_radio)
        platform_layout.addWidget(mac_radio)
        platform_layout.addWidget(linux_radio)
        
        platform_group.setLayout(platform_layout)
        layout.addWidget(platform_group)
        
        # Progress section
        self.progress_label = QLabel("Ready to build")
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(150)
        layout.addWidget(self.log_output)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.build_btn = QPushButton("Build")
        self.build_btn.clicked.connect(self.start_build)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.build_btn)
        button_layout.addWidget(self.close_btn)
        layout.addLayout(button_layout)
        
    def start_build(self):
        """Start the build process"""
        self.build_btn.setEnabled(False)
        self.log_output.clear()
        self.log_output.append("Starting build process...\n")
        
        build_options = {
            'debug_mode': self.debug_check.isChecked(),
            'platform': self.platform_buttons.checkedId()
        }
        
        self.build_thread = BuildThread(self.project_data, build_options)
        self.build_thread.progress.connect(self.update_progress)
        self.build_thread.finished.connect(self.build_finished)
        self.build_thread.start()
        
    def update_progress(self, value, message):
        """Update progress bar and log"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
        self.log_output.append(message)
        
    def build_finished(self, success, message):
        """Handle build completion"""
        self.log_output.append(f"\n{message}")
        self.build_btn.setEnabled(True)
        
        if success:
            self.progress_label.setText("Build completed successfully!")
        else:
            self.progress_label.setText("Build failed!")


class RunGameDialog(QDialog):
    """Dialog for running/testing the game"""
    
    def __init__(self, project_data, parent=None):
        super().__init__(parent)
        self.project_data = project_data
        self.setWindowTitle(f"Run Game - {project_data['name']}")
        self.setModal(False)
        self.setMinimumSize(600, 400)
        self.game_process = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Info label
        info_label = QLabel("Game Runtime")
        info_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        # Game output
        self.game_output = QTextEdit()
        self.game_output.setReadOnly(True)
        layout.addWidget(self.game_output)
        
        # Check if build exists
        build_path = os.path.join(self.project_data['path'], 'build')
        exe_path = os.path.join(build_path, f"{self.project_data['name']}.exe")
        
        if os.path.exists(exe_path):
            self.game_output.append("=" * 50)
            self.game_output.append(f"Found executable: {self.project_data['name']}.exe")
            self.game_output.append("=" * 50)
            self.game_output.append("\nClick 'Launch Game' to start the game executable.")
            self.game_output.append("\nThe game will run in a separate window.")
            self.game_output.append("Close this dialog or the game window to stop.")
        else:
            self.game_output.append("=" * 50)
            self.game_output.append("No Build Found")
            self.game_output.append("=" * 50)
            self.game_output.append("\nThe project has not been built yet.")
            self.game_output.append("\nPlease build the project first (Build > Build Game)")
            self.game_output.append("or press Ctrl+B")
            self.game_output.append("\n" + "=" * 50)
            self.game_output.append("\nProject Preview:")
            self.game_output.append(f"\nProject: {self.project_data['name']}")
            self.game_output.append(f"Version: {self.project_data['version']}")
            
            # Show project contents
            timeline = self.project_data.get('timeline', [])
            chapters = self.project_data.get('story', {}).get('chapters', [])
            characters = self.project_data.get('story', {}).get('characters', [])
            classes = self.project_data.get('gameplay', {}).get('classes', [])
            
            self.game_output.append(f"\nTimeline Events: {len(timeline)}")
            self.game_output.append(f"Chapters: {len(chapters)}")
            self.game_output.append(f"Characters: {len(characters)}")
            self.game_output.append(f"Classes: {len(classes)}")
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.launch_btn = QPushButton("Launch Game")
        self.launch_btn.clicked.connect(self.launch_game)
        self.launch_btn.setEnabled(os.path.exists(exe_path))
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close_and_cleanup)
        
        button_layout.addStretch()
        button_layout.addWidget(self.launch_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
    
    def launch_game(self):
        """Launch the built game executable"""
        build_path = os.path.join(self.project_data['path'], 'build')
        exe_path = os.path.join(build_path, f"{self.project_data['name']}.exe")
        
        if os.path.exists(exe_path):
            try:
                self.game_output.append(f"\n[{datetime.now().strftime('%H:%M:%S')}] Launching game...")
                # Run with console visible for debug output
                self.game_process = subprocess.Popen(
                    [exe_path],
                    cwd=build_path,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
                self.game_output.append(f"[{datetime.now().strftime('%H:%M:%S')}] Game started (PID: {self.game_process.pid})")
                self.game_output.append("\nGame is running in a separate console window.")
                self.game_output.append("Check the console for debug output.")
                self.game_output.append("Close the game window when done.")
                self.launch_btn.setEnabled(False)
            except Exception as e:
                self.game_output.append(f"\n[ERROR] Failed to launch game: {str(e)}")
        else:
            self.game_output.append("\n[ERROR] Executable not found. Please build the project first.")
    
    def close_and_cleanup(self):
        """Close dialog and cleanup any running processes"""
        if self.game_process and self.game_process.poll() is None:
            self.game_output.append(f"\n[{datetime.now().strftime('%H:%M:%S')}] Stopping game...")
            self.game_process.terminate()
            try:
                self.game_process.wait(timeout=3)
            except:
                self.game_process.kill()
        self.accept()
