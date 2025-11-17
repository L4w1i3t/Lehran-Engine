"""
Story Editor for Lehran Engine
Handles chapters, characters, dialogue, and narrative
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                              QListWidget, QGroupBox, QPushButton, QLabel,
                              QLineEdit, QTextEdit, QComboBox, QSpinBox,
                              QTabWidget, QTreeWidget, QTreeWidgetItem,
                              QMessageBox, QFormLayout, QScrollArea)
from PyQt6.QtCore import Qt


class StoryEditor(QWidget):
    """Editor for story and narrative elements"""
    
    def __init__(self):
        super().__init__()
        self.chapters = []
        self.characters = []
        self.dialogues = []
        self.supports = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the story editor UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create tab widget for different story aspects
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Chapters tab
        self.chapters_widget = ChaptersWidget()
        tabs.addTab(self.chapters_widget, "Chapters")
        
        # Characters tab
        self.characters_widget = CharactersWidget()
        tabs.addTab(self.characters_widget, "Characters")
        
        # Dialogue tab
        self.dialogue_widget = DialogueWidget()
        tabs.addTab(self.dialogue_widget, "Dialogue")
        
        # Supports tab
        self.supports_widget = SupportsWidget()
        tabs.addTab(self.supports_widget, "Support Conversations")
        
    def get_data(self):
        """Get all story data"""
        return {
            'chapters': self.chapters_widget.get_data(),
            'characters': self.characters_widget.get_data(),
            'dialogues': self.dialogue_widget.get_data(),
            'supports': self.supports_widget.get_data()
        }
        
    def load_data(self, data):
        """Load story data"""
        self.chapters_widget.load_data(data.get('chapters', []))
        self.characters_widget.load_data(data.get('characters', []))
        self.dialogue_widget.load_data(data.get('dialogues', []))
        self.supports_widget.load_data(data.get('supports', []))


class ChaptersWidget(QWidget):
    """Widget for managing game chapters"""
    
    def __init__(self):
        super().__init__()
        self.chapters = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the chapters UI"""
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Left side - chapter list
        left_layout = QVBoxLayout()
        
        left_layout.addWidget(QLabel("Chapters:"))
        self.chapter_list = QListWidget()
        self.chapter_list.currentRowChanged.connect(self.on_chapter_selected)
        left_layout.addWidget(self.chapter_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Chapter")
        add_btn.clicked.connect(self.add_chapter)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_chapter)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        left_layout.addLayout(btn_layout)
        
        layout.addLayout(left_layout, 1)
        
        # Right side - chapter details
        right_layout = QVBoxLayout()
        
        details_group = QGroupBox("Chapter Details")
        details_layout = QFormLayout()
        
        self.chapter_name = QLineEdit()
        self.chapter_number = QSpinBox()
        self.chapter_number.setMinimum(1)
        self.chapter_number.setMaximum(999)
        self.chapter_objective = QLineEdit()
        self.chapter_description = QTextEdit()
        self.chapter_description.setMaximumHeight(100)
        self.chapter_map = QLineEdit()
        
        details_layout.addRow("Chapter Name:", self.chapter_name)
        details_layout.addRow("Chapter Number:", self.chapter_number)
        details_layout.addRow("Objective:", self.chapter_objective)
        details_layout.addRow("Description:", self.chapter_description)
        details_layout.addRow("Map File:", self.chapter_map)
        
        details_group.setLayout(details_layout)
        right_layout.addWidget(details_group)
        
        # Events section
        events_group = QGroupBox("Chapter Events")
        events_layout = QVBoxLayout()
        
        self.events_list = QListWidget()
        events_layout.addWidget(self.events_list)
        
        events_btn_layout = QHBoxLayout()
        add_event_btn = QPushButton("Add Event")
        edit_event_btn = QPushButton("Edit Event")
        remove_event_btn = QPushButton("Remove Event")
        events_btn_layout.addWidget(add_event_btn)
        events_btn_layout.addWidget(edit_event_btn)
        events_btn_layout.addWidget(remove_event_btn)
        events_layout.addLayout(events_btn_layout)
        
        events_group.setLayout(events_layout)
        right_layout.addWidget(events_group)
        
        right_layout.addStretch()
        layout.addLayout(right_layout, 2)
        
    def add_chapter(self):
        """Add a new chapter"""
        chapter_num = len(self.chapters) + 1
        chapter = {
            'name': f'Chapter {chapter_num}',
            'number': chapter_num,
            'objective': 'Defeat all enemies',
            'description': '',
            'map': '',
            'events': []
        }
        self.chapters.append(chapter)
        self.chapter_list.addItem(f"Ch.{chapter_num}: {chapter['name']}")
        
    def remove_chapter(self):
        """Remove selected chapter"""
        row = self.chapter_list.currentRow()
        if row >= 0:
            self.chapters.pop(row)
            self.chapter_list.takeItem(row)
            
    def on_chapter_selected(self, index):
        """Handle chapter selection"""
        if 0 <= index < len(self.chapters):
            chapter = self.chapters[index]
            self.chapter_name.setText(chapter['name'])
            self.chapter_number.setValue(chapter['number'])
            self.chapter_objective.setText(chapter['objective'])
            self.chapter_description.setPlainText(chapter['description'])
            self.chapter_map.setText(chapter['map'])
            
    def get_data(self):
        """Get chapters data"""
        return self.chapters
        
    def load_data(self, chapters):
        """Load chapters data"""
        self.chapters = chapters
        self.chapter_list.clear()
        for ch in chapters:
            self.chapter_list.addItem(f"Ch.{ch['number']}: {ch['name']}")


class CharactersWidget(QWidget):
    """Widget for managing characters"""
    
    def __init__(self):
        super().__init__()
        self.characters = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the characters UI"""
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Left side - character list
        left_layout = QVBoxLayout()
        
        left_layout.addWidget(QLabel("Characters:"))
        self.character_list = QListWidget()
        self.character_list.currentRowChanged.connect(self.on_character_selected)
        left_layout.addWidget(self.character_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Character")
        add_btn.clicked.connect(self.add_character)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_character)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        left_layout.addLayout(btn_layout)
        
        layout.addLayout(left_layout, 1)
        
        # Right side - character details
        right_layout = QVBoxLayout()
        
        details_group = QGroupBox("Character Details")
        details_layout = QFormLayout()
        
        self.char_name = QLineEdit()
        self.char_title = QLineEdit()
        self.char_affiliation = QComboBox()
        self.char_affiliation.addItems(["Player", "Enemy", "Ally", "Other"])
        self.char_description = QTextEdit()
        self.char_description.setMaximumHeight(120)
        self.char_bio = QTextEdit()
        self.char_bio.setMaximumHeight(120)
        
        details_layout.addRow("Name:", self.char_name)
        details_layout.addRow("Title:", self.char_title)
        details_layout.addRow("Affiliation:", self.char_affiliation)
        details_layout.addRow("Description:", self.char_description)
        details_layout.addRow("Biography:", self.char_bio)
        
        details_group.setLayout(details_layout)
        right_layout.addWidget(details_group)
        
        right_layout.addStretch()
        layout.addLayout(right_layout, 2)
        
    def add_character(self):
        """Add a new character"""
        character = {
            'name': 'New Character',
            'title': '',
            'affiliation': 'Player',
            'description': '',
            'biography': ''
        }
        self.characters.append(character)
        self.character_list.addItem(character['name'])
        
    def remove_character(self):
        """Remove selected character"""
        row = self.character_list.currentRow()
        if row >= 0:
            self.characters.pop(row)
            self.character_list.takeItem(row)
            
    def on_character_selected(self, index):
        """Handle character selection"""
        if 0 <= index < len(self.characters):
            char = self.characters[index]
            self.char_name.setText(char['name'])
            self.char_title.setText(char['title'])
            self.char_affiliation.setCurrentText(char['affiliation'])
            self.char_description.setPlainText(char['description'])
            self.char_bio.setPlainText(char['biography'])
            
    def get_data(self):
        """Get characters data"""
        return self.characters
        
    def load_data(self, characters):
        """Load characters data"""
        self.characters = characters
        self.character_list.clear()
        for char in characters:
            self.character_list.addItem(char['name'])


class DialogueWidget(QWidget):
    """Widget for managing dialogue"""
    
    def __init__(self):
        super().__init__()
        self.dialogues = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dialogue UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        layout.addWidget(QLabel("Dialogue scenes will be managed here"))
        layout.addWidget(QLabel("Features: Scene creation, speaker selection, text entry, branching"))
        
        # Placeholder for future implementation
        self.dialogue_list = QListWidget()
        layout.addWidget(self.dialogue_list)
        
    def get_data(self):
        return self.dialogues
        
    def load_data(self, dialogues):
        self.dialogues = dialogues


class SupportsWidget(QWidget):
    """Widget for managing support conversations"""
    
    def __init__(self):
        super().__init__()
        self.supports = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the supports UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        layout.addWidget(QLabel("Support conversation system"))
        layout.addWidget(QLabel("Features: Character pairs, support levels (C/B/A/S), conversation text"))
        
        # Placeholder for future implementation
        self.supports_list = QListWidget()
        layout.addWidget(self.supports_list)
        
    def get_data(self):
        return self.supports
        
    def load_data(self, supports):
        self.supports = supports
