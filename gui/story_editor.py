"""
Story Editor for Lehran Engine
Handles chapters, characters, dialogue, and narrative
"""

import random
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                              QListWidget, QGroupBox, QPushButton, QLabel,
                              QLineEdit, QTextEdit, QComboBox, QSpinBox,
                              QTabWidget, QTreeWidget, QTreeWidgetItem,
                              QMessageBox, QFormLayout, QScrollArea,
                              QFileDialog)
from PyQt6.QtCore import Qt


def generate_character_id():
    """Generate a random 8-digit ID using a simple seeded RNG"""
    # Use current time and random state for seed
    seed = random.randint(0, 0xFFFFFFFF)
    
    # Simple Mulberry32-inspired generator
    def mulberry32():
        nonlocal seed
        seed = (seed + 0x6D2B79F5) & 0xFFFFFFFF
        t = seed
        t = ((t ^ (t >> 15)) * (t | 1)) & 0xFFFFFFFF
        t = (t ^ (t + ((t ^ (t >> 7)) * (t | 61)))) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) >> 0) & 0xFFFFFFFF
    
    # Generate 8-digit number (10000000 to 99999999)
    char_id = (mulberry32() % 90000000) + 10000000
    return str(char_id)


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
        
        # Supports tab
        self.supports_widget = SupportsWidget()
        tabs.addTab(self.supports_widget, "Support Conversations")
        
    def get_data(self):
        """Get all story data"""
        return {
            'chapters': self.chapters_widget.get_data(),
            'characters': self.characters_widget.get_data(),
            'supports': self.supports_widget.get_data()
        }
        
    def load_data(self, data):
        """Load story data"""
        # Block signals during load to prevent triggering change detection
        self.chapters_widget.chapter_list.blockSignals(True)
        self.characters_widget.character_list.blockSignals(True)
        self.supports_widget.supports_list.blockSignals(True)
        
        try:
            self.chapters_widget.load_data(data.get('chapters', []))
            self.characters_widget.load_data(data.get('characters', []))
            self.supports_widget.load_data(data.get('supports', []))
        finally:
            # Always restore signals
            self.chapters_widget.chapter_list.blockSignals(False)
            self.characters_widget.character_list.blockSignals(False)
            self.supports_widget.supports_list.blockSignals(False)


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
        
        # Right side - chapter details (scrollable)
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        
        details_group = QGroupBox("Chapter Details")
        details_layout = QFormLayout()
        
        self.chapter_name = QLineEdit()
        self.chapter_number = QSpinBox()
        self.chapter_number.setMinimum(-1)
        self.chapter_number.setMaximum(999)
        self.chapter_number.setSpecialValueText("Pre-Prologue")
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
        
        # Create tabs for different event types
        events_tabs = QTabWidget()
        
        # Pre-Chapter Story Events
        pre_events_widget = QWidget()
        pre_events_layout = QVBoxLayout()
        pre_events_widget.setLayout(pre_events_layout)
        
        pre_info = QLabel("Story events that play BEFORE the chapter/mission starts")
        pre_info.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        pre_events_layout.addWidget(pre_info)
        
        self.pre_events_list = QListWidget()
        self.pre_events_list.currentRowChanged.connect(lambda idx: self.on_event_selected(idx, 'pre'))
        pre_events_layout.addWidget(self.pre_events_list)
        
        pre_btn_layout = QHBoxLayout()
        add_pre_btn = QPushButton("Add Event")
        add_pre_btn.clicked.connect(lambda: self.add_event('pre'))
        remove_pre_btn = QPushButton("Remove")
        remove_pre_btn.clicked.connect(lambda: self.remove_event('pre'))
        move_pre_up = QPushButton("↑")
        move_pre_up.setMaximumWidth(40)
        move_pre_up.clicked.connect(lambda: self.move_event_up('pre'))
        move_pre_down = QPushButton("↓")
        move_pre_down.setMaximumWidth(40)
        move_pre_down.clicked.connect(lambda: self.move_event_down('pre'))
        pre_btn_layout.addWidget(add_pre_btn)
        pre_btn_layout.addWidget(remove_pre_btn)
        pre_btn_layout.addWidget(move_pre_up)
        pre_btn_layout.addWidget(move_pre_down)
        pre_events_layout.addLayout(pre_btn_layout)
        
        events_tabs.addTab(pre_events_widget, "Pre-Chapter Story")
        
        # Gameplay Events (during mission)
        gameplay_events_widget = QWidget()
        gameplay_events_layout = QVBoxLayout()
        gameplay_events_widget.setLayout(gameplay_events_layout)
        
        gameplay_info = QLabel("Events that trigger DURING the mission/battle")
        gameplay_info.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        gameplay_events_layout.addWidget(gameplay_info)
        
        self.gameplay_events_list = QListWidget()
        self.gameplay_events_list.currentRowChanged.connect(lambda idx: self.on_event_selected(idx, 'gameplay'))
        gameplay_events_layout.addWidget(self.gameplay_events_list)
        
        gameplay_btn_layout = QHBoxLayout()
        add_gameplay_btn = QPushButton("Add Event")
        add_gameplay_btn.clicked.connect(lambda: self.add_event('gameplay'))
        remove_gameplay_btn = QPushButton("Remove")
        remove_gameplay_btn.clicked.connect(lambda: self.remove_event('gameplay'))
        move_gameplay_up = QPushButton("↑")
        move_gameplay_up.setMaximumWidth(40)
        move_gameplay_up.clicked.connect(lambda: self.move_event_up('gameplay'))
        move_gameplay_down = QPushButton("↓")
        move_gameplay_down.setMaximumWidth(40)
        move_gameplay_down.clicked.connect(lambda: self.move_event_down('gameplay'))
        gameplay_btn_layout.addWidget(add_gameplay_btn)
        gameplay_btn_layout.addWidget(remove_gameplay_btn)
        gameplay_btn_layout.addWidget(move_gameplay_up)
        gameplay_btn_layout.addWidget(move_gameplay_down)
        gameplay_events_layout.addLayout(gameplay_btn_layout)
        
        events_tabs.addTab(gameplay_events_widget, "Gameplay Events")
        
        # Post-Chapter Story Events
        post_events_widget = QWidget()
        post_events_layout = QVBoxLayout()
        post_events_widget.setLayout(post_events_layout)
        
        post_info = QLabel("Story events that play AFTER the chapter/mission completes")
        post_info.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        post_events_layout.addWidget(post_info)
        
        self.post_events_list = QListWidget()
        self.post_events_list.currentRowChanged.connect(lambda idx: self.on_event_selected(idx, 'post'))
        post_events_layout.addWidget(self.post_events_list)
        
        post_btn_layout = QHBoxLayout()
        add_post_btn = QPushButton("Add Event")
        add_post_btn.clicked.connect(lambda: self.add_event('post'))
        remove_post_btn = QPushButton("Remove")
        remove_post_btn.clicked.connect(lambda: self.remove_event('post'))
        move_post_up = QPushButton("↑")
        move_post_up.setMaximumWidth(40)
        move_post_up.clicked.connect(lambda: self.move_event_up('post'))
        move_post_down = QPushButton("↓")
        move_post_down.setMaximumWidth(40)
        move_post_down.clicked.connect(lambda: self.move_event_down('post'))
        post_btn_layout.addWidget(add_post_btn)
        post_btn_layout.addWidget(remove_post_btn)
        post_btn_layout.addWidget(move_post_up)
        post_btn_layout.addWidget(move_post_down)
        post_events_layout.addLayout(post_btn_layout)
        
        events_tabs.addTab(post_events_widget, "Post-Chapter Story")
        
        right_layout.addWidget(events_tabs)
        
        # Event editor (shared by all tabs) - now includes full scene details
        event_editor_group = QGroupBox("Edit Selected Event")
        event_editor_layout = QVBoxLayout()
        
        # Show which event is being edited
        self.current_event_label = QLabel("No event selected")
        self.current_event_label.setStyleSheet("font-weight: bold; color: #4682B4; padding: 5px; background-color: rgba(70, 130, 180, 0.1); border-radius: 3px;")
        self.current_event_label.setWordWrap(True)
        event_editor_layout.addWidget(self.current_event_label)
        
        # Basic event info
        basic_form = QFormLayout()
        
        self.event_type = QComboBox()
        self.event_type.currentTextChanged.connect(self.update_current_event)
        
        self.event_name = QLineEdit()
        self.event_name.textChanged.connect(self.update_current_event)
        
        self.event_trigger = QComboBox()
        self.event_trigger.currentTextChanged.connect(self.update_current_event)
        
        basic_form.addRow("Event Type:", self.event_type)
        basic_form.addRow("Event Name:", self.event_name)
        basic_form.addRow("Trigger:", self.event_trigger)
        
        event_editor_layout.addLayout(basic_form)
        
        # Scene settings (for story events)
        scene_settings_group = QGroupBox("Scene Settings (Optional)")
        scene_settings_layout = QFormLayout()
        
        self.event_background = QLineEdit()
        self.event_background.setPlaceholderText("e.g., backgrounds/throne_room.png")
        self.event_background.textChanged.connect(self.update_current_event)
        
        bg_btn_layout = QHBoxLayout()
        bg_btn_layout.addWidget(self.event_background)
        browse_bg_btn = QPushButton("Browse...")
        browse_bg_btn.clicked.connect(self.browse_event_background)
        bg_btn_layout.addWidget(browse_bg_btn)
        
        self.event_music = QLineEdit()
        self.event_music.setPlaceholderText("e.g., bgm/sad_theme.ogg")
        self.event_music.textChanged.connect(self.update_current_event)
        
        music_btn_layout = QHBoxLayout()
        music_btn_layout.addWidget(self.event_music)
        browse_music_btn = QPushButton("Browse...")
        browse_music_btn.clicked.connect(self.browse_event_music)
        music_btn_layout.addWidget(browse_music_btn)
        
        scene_settings_layout.addRow("Background:", bg_btn_layout)
        scene_settings_layout.addRow("Music:", music_btn_layout)
        
        scene_settings_group.setLayout(scene_settings_layout)
        event_editor_layout.addWidget(scene_settings_group)
        
        # Dialogue lines
        dialogue_group = QGroupBox("Dialogue Lines (Optional)")
        dialogue_layout = QVBoxLayout()
        
        self.event_dialogue_list = QListWidget()
        self.event_dialogue_list.setMaximumHeight(120)
        self.event_dialogue_list.currentRowChanged.connect(self.on_dialogue_line_selected)
        dialogue_layout.addWidget(self.event_dialogue_list)
        
        # Dialogue line buttons
        dialogue_btn_layout = QHBoxLayout()
        add_line_btn = QPushButton("Add Line")
        add_line_btn.clicked.connect(self.add_dialogue_line)
        remove_line_btn = QPushButton("Remove Line")
        remove_line_btn.clicked.connect(self.remove_dialogue_line)
        move_line_up_btn = QPushButton("↑")
        move_line_up_btn.setMaximumWidth(40)
        move_line_up_btn.clicked.connect(self.move_dialogue_line_up)
        move_line_down_btn = QPushButton("↓")
        move_line_down_btn.setMaximumWidth(40)
        move_line_down_btn.clicked.connect(self.move_dialogue_line_down)
        
        dialogue_btn_layout.addWidget(add_line_btn)
        dialogue_btn_layout.addWidget(remove_line_btn)
        dialogue_btn_layout.addWidget(move_line_up_btn)
        dialogue_btn_layout.addWidget(move_line_down_btn)
        dialogue_layout.addLayout(dialogue_btn_layout)
        
        # Dialogue line editor
        line_form = QFormLayout()
        
        self.dialogue_speaker = QLineEdit()
        self.dialogue_speaker.setPlaceholderText("Character name or leave empty for narration")
        self.dialogue_speaker.textChanged.connect(self.update_current_dialogue_line)
        
        self.dialogue_portrait = QLineEdit()
        self.dialogue_portrait.setPlaceholderText("Optional: portraits/character.png")
        self.dialogue_portrait.textChanged.connect(self.update_current_dialogue_line)
        
        portrait_btn_layout = QHBoxLayout()
        portrait_btn_layout.addWidget(self.dialogue_portrait)
        browse_portrait_btn = QPushButton("Browse...")
        browse_portrait_btn.clicked.connect(self.browse_dialogue_portrait)
        portrait_btn_layout.addWidget(browse_portrait_btn)
        
        self.dialogue_text = QTextEdit()
        self.dialogue_text.setMaximumHeight(60)
        self.dialogue_text.setPlaceholderText("Dialogue text...")
        self.dialogue_text.textChanged.connect(self.update_current_dialogue_line)
        
        line_form.addRow("Speaker:", self.dialogue_speaker)
        line_form.addRow("Portrait:", portrait_btn_layout)
        line_form.addRow("Text:", self.dialogue_text)
        
        dialogue_layout.addLayout(line_form)
        
        dialogue_group.setLayout(dialogue_layout)
        event_editor_layout.addWidget(dialogue_group)
        
        # Event description/notes
        self.event_description = QTextEdit()
        self.event_description.setMaximumHeight(60)
        self.event_description.setPlaceholderText("Event description/notes...")
        self.event_description.textChanged.connect(self.update_current_event)
        event_editor_layout.addWidget(QLabel("Description/Notes:"))
        event_editor_layout.addWidget(self.event_description)
        
        event_editor_group.setLayout(event_editor_layout)
        right_layout.addWidget(event_editor_group)
        
        right_layout.addStretch()
        right_scroll.setWidget(right_widget)
        layout.addWidget(right_scroll, 2)
        
        self._updating = False
        self._current_event_category = None  # Track which category is being edited
        
        # Set event type options based on category
        self.update_event_type_options()
        
    def update_event_type_options(self):
        """Update event type dropdown based on current category"""
        # This will be called when switching between event categories
        pass
        
    def add_chapter(self):
        """Add a new chapter"""
        chapter_num = len(self.chapters) + 1
        chapter = {
            'name': f'Chapter {chapter_num}',
            'number': chapter_num,
            'objective': 'Defeat all enemies',
            'description': '',
            'map': '',
            'pre_events': [],      # Story events before mission
            'gameplay_events': [], # Events during battle
            'post_events': []      # Story events after mission
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
            self._updating = True
            
            chapter = self.chapters[index]
            
            # Ensure chapter has new event structure
            if 'events' in chapter and 'pre_events' not in chapter:
                # Migrate old structure to new
                chapter['pre_events'] = []
                chapter['gameplay_events'] = chapter.get('events', [])
                chapter['post_events'] = []
                del chapter['events']
            
            # Ensure all event arrays exist
            if 'pre_events' not in chapter:
                chapter['pre_events'] = []
            if 'gameplay_events' not in chapter:
                chapter['gameplay_events'] = []
            if 'post_events' not in chapter:
                chapter['post_events'] = []
            
            self.chapter_name.setText(chapter['name'])
            self.chapter_number.setValue(chapter['number'])
            self.chapter_objective.setText(chapter['objective'])
            self.chapter_description.setPlainText(chapter['description'])
            self.chapter_map.setText(chapter['map'])
            
            # Load all event lists
            self.refresh_all_event_lists()
            
            self._updating = False
            
    def refresh_all_event_lists(self):
        """Refresh all three event lists"""
        chapter_idx = self.chapter_list.currentRow()
        if 0 <= chapter_idx < len(self.chapters):
            chapter = self.chapters[chapter_idx]
            
            # Pre-events
            self.pre_events_list.clear()
            for i, event in enumerate(chapter.get('pre_events', []), 1):
                event_name = event.get('name', 'Unnamed Event')
                event_type = event.get('type', 'Cutscene')
                self.pre_events_list.addItem(f"[{i}] {event_type}: {event_name}")
            
            # Gameplay events
            self.gameplay_events_list.clear()
            for i, event in enumerate(chapter.get('gameplay_events', []), 1):
                event_name = event.get('name', 'Unnamed Event')
                event_type = event.get('type', 'Unit Spawn')
                self.gameplay_events_list.addItem(f"[{i}] {event_type}: {event_name}")
            
            # Post-events
            self.post_events_list.clear()
            for i, event in enumerate(chapter.get('post_events', []), 1):
                event_name = event.get('name', 'Unnamed Event')
                event_type = event.get('type', 'Cutscene')
                self.post_events_list.addItem(f"[{i}] {event_type}: {event_name}")
            
    def add_event(self, category):
        """Add a new event to current chapter"""
        index = self.chapter_list.currentRow()
        if 0 <= index < len(self.chapters):
            chapter = self.chapters[index]
            
            # Set default type based on category
            if category == 'pre' or category == 'post':
                event = {
                    'type': 'Cutscene',
                    'name': 'New Story Event',
                    'trigger': 'Auto',
                    'description': '',
                    'background': '',
                    'music': '',
                    'dialogue': []
                }
            else:  # gameplay
                event = {
                    'type': 'Unit Spawn',
                    'name': 'New Gameplay Event',
                    'trigger': 'Turn',
                    'description': '',
                    'background': '',
                    'music': '',
                    'dialogue': []
                }
            
            event_key = f'{category}_events'
            if event_key not in chapter:
                chapter[event_key] = []
            chapter[event_key].append(event)
            
            self.refresh_all_event_lists()
            
    def remove_event(self, category):
        """Remove selected event"""
        chapter_idx = self.chapter_list.currentRow()
        if 0 <= chapter_idx < len(self.chapters):
            event_list = self._get_event_list_widget(category)
            event_idx = event_list.currentRow()
            
            if event_idx >= 0:
                chapter = self.chapters[chapter_idx]
                event_key = f'{category}_events'
                if event_idx < len(chapter[event_key]):
                    chapter[event_key].pop(event_idx)
                    self.refresh_all_event_lists()
                
    def move_event_up(self, category):
        """Move selected event up"""
        chapter_idx = self.chapter_list.currentRow()
        if 0 <= chapter_idx < len(self.chapters):
            event_list = self._get_event_list_widget(category)
            event_idx = event_list.currentRow()
            
            if event_idx > 0:
                chapter = self.chapters[chapter_idx]
                event_key = f'{category}_events'
                events = chapter[event_key]
                events[event_idx], events[event_idx-1] = events[event_idx-1], events[event_idx]
                self.refresh_all_event_lists()
                event_list.setCurrentRow(event_idx - 1)
            
    def move_event_down(self, category):
        """Move selected event down"""
        chapter_idx = self.chapter_list.currentRow()
        if 0 <= chapter_idx < len(self.chapters):
            event_list = self._get_event_list_widget(category)
            event_idx = event_list.currentRow()
            
            chapter = self.chapters[chapter_idx]
            event_key = f'{category}_events'
            events = chapter[event_key]
            
            if 0 <= event_idx < len(events) - 1:
                events[event_idx], events[event_idx+1] = events[event_idx+1], events[event_idx]
                self.refresh_all_event_lists()
                event_list.setCurrentRow(event_idx + 1)
                
    def _get_event_list_widget(self, category):
        """Get the appropriate event list widget"""
        if category == 'pre':
            return self.pre_events_list
        elif category == 'gameplay':
            return self.gameplay_events_list
        else:  # post
            return self.post_events_list
                
    def on_event_selected(self, index, category):
        """Handle event selection"""
        chapter_idx = self.chapter_list.currentRow()
        if 0 <= chapter_idx < len(self.chapters):
            chapter = self.chapters[chapter_idx]
            event_key = f'{category}_events'
            
            if 0 <= index < len(chapter.get(event_key, [])):
                self._updating = True
                self._current_event_category = category
                
                event = chapter[event_key][index]
                
                # Update label to show which event is being edited
                chapter_name = chapter.get('name', 'Unnamed Chapter')
                event_name = event.get('name', 'Unnamed Event')
                category_name = {
                    'pre': 'Pre-Chapter',
                    'gameplay': 'Gameplay',
                    'post': 'Post-Chapter'
                }.get(category, category)
                
                self.current_event_label.setText(
                    f"Editing: {chapter_name} → {category_name} → {event_name}\n"
                    f"Dialogue lines below belong to this event"
                )
                
                # Ensure event has new fields
                if 'background' not in event:
                    event['background'] = ''
                if 'music' not in event:
                    event['music'] = ''
                if 'dialogue' not in event:
                    event['dialogue'] = []
                
                # Update event type options based on category
                self.event_type.clear()
                if category == 'pre' or category == 'post':
                    self.event_type.addItems(["Cutscene", "Dialogue", "Narration", "Award", "Other"])
                    self.event_trigger.clear()
                    self.event_trigger.addItems(["Auto", "Custom"])
                else:  # gameplay
                    self.event_type.addItems(["Unit Spawn", "Dialogue", "Trigger", "Reinforcements", "Item Drop", "Condition", "Other"])
                    self.event_trigger.clear()
                    self.event_trigger.addItems(["Turn", "Position", "Talk", "Enemy Defeated", "HP Threshold", "Custom"])
                
                self.event_type.setCurrentText(event.get('type', self.event_type.itemText(0)))
                self.event_name.setText(event.get('name', ''))
                self.event_trigger.setCurrentText(event.get('trigger', self.event_trigger.itemText(0)))
                self.event_description.setPlainText(event.get('description', ''))
                self.event_background.setText(event.get('background', ''))
                self.event_music.setText(event.get('music', ''))
                
                # Load dialogue lines
                self.event_dialogue_list.clear()
                for i, line in enumerate(event.get('dialogue', []), 1):
                    speaker = line.get('speaker', '')
                    text = line.get('text', '')
                    preview = text[:30] + '...' if len(text) > 30 else text
                    self.event_dialogue_list.addItem(f"[{i}] {speaker}: {preview}")
                
                self._updating = False
                
    def update_current_event(self):
        """Update current event with form data"""
        if self._updating or self._current_event_category is None:
            return
        
        chapter_idx = self.chapter_list.currentRow()
        if 0 <= chapter_idx < len(self.chapters):
            chapter = self.chapters[chapter_idx]
            event_key = f'{self._current_event_category}_events'
            event_list = self._get_event_list_widget(self._current_event_category)
            event_idx = event_list.currentRow()
            
            if 0 <= event_idx < len(chapter.get(event_key, [])):
                event = chapter[event_key][event_idx]
                event['type'] = self.event_type.currentText()
                event['name'] = self.event_name.text()
                event['trigger'] = self.event_trigger.currentText()
                event['description'] = self.event_description.toPlainText()
                event['background'] = self.event_background.text()
                event['music'] = self.event_music.text()
                
                # Update list display
                event_list.item(event_idx).setText(f"[{event_idx + 1}] {event['type']}: {event['name']}")
                
    def add_dialogue_line(self):
        """Add a dialogue line to current event"""
        if self._current_event_category is None:
            return
            
        chapter_idx = self.chapter_list.currentRow()
        if 0 <= chapter_idx < len(self.chapters):
            chapter = self.chapters[chapter_idx]
            event_key = f'{self._current_event_category}_events'
            event_list = self._get_event_list_widget(self._current_event_category)
            event_idx = event_list.currentRow()
            
            if 0 <= event_idx < len(chapter.get(event_key, [])):
                event = chapter[event_key][event_idx]
                if 'dialogue' not in event:
                    event['dialogue'] = []
                
                line = {
                    'speaker': '',
                    'portrait': '',
                    'text': ''
                }
                event['dialogue'].append(line)
                
                line_num = len(event['dialogue'])
                self.event_dialogue_list.addItem(f"[{line_num}] : ")
                
    def remove_dialogue_line(self):
        """Remove selected dialogue line"""
        if self._current_event_category is None:
            return
            
        chapter_idx = self.chapter_list.currentRow()
        line_idx = self.event_dialogue_list.currentRow()
        
        if 0 <= chapter_idx < len(self.chapters) and line_idx >= 0:
            chapter = self.chapters[chapter_idx]
            event_key = f'{self._current_event_category}_events'
            event_list = self._get_event_list_widget(self._current_event_category)
            event_idx = event_list.currentRow()
            
            if 0 <= event_idx < len(chapter.get(event_key, [])):
                event = chapter[event_key][event_idx]
                if line_idx < len(event.get('dialogue', [])):
                    event['dialogue'].pop(line_idx)
                    self.refresh_dialogue_lines()
                    
    def move_dialogue_line_up(self):
        """Move selected dialogue line up"""
        if self._current_event_category is None:
            return
            
        chapter_idx = self.chapter_list.currentRow()
        line_idx = self.event_dialogue_list.currentRow()
        
        if 0 <= chapter_idx < len(self.chapters) and line_idx > 0:
            chapter = self.chapters[chapter_idx]
            event_key = f'{self._current_event_category}_events'
            event_list = self._get_event_list_widget(self._current_event_category)
            event_idx = event_list.currentRow()
            
            if 0 <= event_idx < len(chapter.get(event_key, [])):
                event = chapter[event_key][event_idx]
                dialogue = event.get('dialogue', [])
                dialogue[line_idx], dialogue[line_idx-1] = dialogue[line_idx-1], dialogue[line_idx]
                self.refresh_dialogue_lines()
                self.event_dialogue_list.setCurrentRow(line_idx - 1)
                
    def move_dialogue_line_down(self):
        """Move selected dialogue line down"""
        if self._current_event_category is None:
            return
            
        chapter_idx = self.chapter_list.currentRow()
        line_idx = self.event_dialogue_list.currentRow()
        
        if 0 <= chapter_idx < len(self.chapters):
            chapter = self.chapters[chapter_idx]
            event_key = f'{self._current_event_category}_events'
            event_list = self._get_event_list_widget(self._current_event_category)
            event_idx = event_list.currentRow()
            
            if 0 <= event_idx < len(chapter.get(event_key, [])):
                event = chapter[event_key][event_idx]
                dialogue = event.get('dialogue', [])
                if 0 <= line_idx < len(dialogue) - 1:
                    dialogue[line_idx], dialogue[line_idx+1] = dialogue[line_idx+1], dialogue[line_idx]
                    self.refresh_dialogue_lines()
                    self.event_dialogue_list.setCurrentRow(line_idx + 1)
                    
    def refresh_dialogue_lines(self):
        """Refresh the dialogue lines display"""
        if self._current_event_category is None:
            return
            
        chapter_idx = self.chapter_list.currentRow()
        current = self.event_dialogue_list.currentRow()
        
        if 0 <= chapter_idx < len(self.chapters):
            chapter = self.chapters[chapter_idx]
            event_key = f'{self._current_event_category}_events'
            event_list = self._get_event_list_widget(self._current_event_category)
            event_idx = event_list.currentRow()
            
            if 0 <= event_idx < len(chapter.get(event_key, [])):
                event = chapter[event_key][event_idx]
                self.event_dialogue_list.clear()
                for i, line in enumerate(event.get('dialogue', []), 1):
                    speaker = line.get('speaker', '')
                    text = line.get('text', '')
                    preview = text[:30] + '...' if len(text) > 30 else text
                    self.event_dialogue_list.addItem(f"[{i}] {speaker}: {preview}")
                
                if 0 <= current < len(event.get('dialogue', [])):
                    self.event_dialogue_list.setCurrentRow(current)
                    
    def on_dialogue_line_selected(self, index):
        """Handle dialogue line selection"""
        if self._current_event_category is None:
            return
            
        chapter_idx = self.chapter_list.currentRow()
        if 0 <= chapter_idx < len(self.chapters):
            chapter = self.chapters[chapter_idx]
            event_key = f'{self._current_event_category}_events'
            event_list = self._get_event_list_widget(self._current_event_category)
            event_idx = event_list.currentRow()
            
            if 0 <= event_idx < len(chapter.get(event_key, [])):
                event = chapter[event_key][event_idx]
                dialogue = event.get('dialogue', [])
                if 0 <= index < len(dialogue):
                    self._updating = True
                    
                    line = dialogue[index]
                    self.dialogue_speaker.setText(line.get('speaker', ''))
                    self.dialogue_portrait.setText(line.get('portrait', ''))
                    self.dialogue_text.setPlainText(line.get('text', ''))
                    
                    self._updating = False
                    
    def update_current_dialogue_line(self):
        """Update current dialogue line with form data"""
        if self._updating or self._current_event_category is None:
            return
            
        chapter_idx = self.chapter_list.currentRow()
        line_idx = self.event_dialogue_list.currentRow()
        
        if 0 <= chapter_idx < len(self.chapters):
            chapter = self.chapters[chapter_idx]
            event_key = f'{self._current_event_category}_events'
            event_list = self._get_event_list_widget(self._current_event_category)
            event_idx = event_list.currentRow()
            
            if 0 <= event_idx < len(chapter.get(event_key, [])):
                event = chapter[event_key][event_idx]
                dialogue = event.get('dialogue', [])
                if 0 <= line_idx < len(dialogue):
                    line = dialogue[line_idx]
                    line['speaker'] = self.dialogue_speaker.text()
                    line['portrait'] = self.dialogue_portrait.text()
                    line['text'] = self.dialogue_text.toPlainText()
                    
                    # Update list display
                    speaker = line['speaker']
                    text = line['text']
                    preview = text[:30] + '...' if len(text) > 30 else text
                    self.event_dialogue_list.item(line_idx).setText(f"[{line_idx + 1}] {speaker}: {preview}")
                    
    def browse_event_background(self):
        """Browse for background image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Background Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)"
        )
        if file_path:
            self.event_background.setText(file_path)
            
    def browse_event_music(self):
        """Browse for music file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Music File",
            "",
            "Audio Files (*.ogg *.mp3 *.wav);;All Files (*.*)"
        )
        if file_path:
            self.event_music.setText(file_path)
            
    def browse_dialogue_portrait(self):
        """Browse for portrait image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Portrait Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)"
        )
        if file_path:
            self.dialogue_portrait.setText(file_path)
            
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
        
        # Right side - character details (scrollable)
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        
        # Use scroll area for character details
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(right_widget)
        
        details_group = QGroupBox("Character Details")
        details_layout = QFormLayout()
        
        # Character ID (read-only, auto-generated)
        self.char_id = QLineEdit()
        self.char_id.setReadOnly(True)
        self.char_id.setStyleSheet("background-color: #f0f0f0; color: #666;")
        self.char_id.setPlaceholderText("Auto-generated")
        
        self.char_name = QLineEdit()
        self.char_name.textChanged.connect(self.update_current_character)
        
        self.char_title = QLineEdit()
        self.char_title.textChanged.connect(self.update_current_character)
        
        self.char_affiliation = QComboBox()
        self.char_affiliation.addItems(["Player", "Enemy", "Ally", "Other"])
        self.char_affiliation.currentTextChanged.connect(self.update_current_character)
        
        self.char_description = QTextEdit()
        self.char_description.setMaximumHeight(120)
        self.char_description.textChanged.connect(self.update_current_character)
        
        self.char_bio = QTextEdit()
        self.char_bio.setMaximumHeight(120)
        self.char_bio.textChanged.connect(self.update_current_character)
        
        details_layout.addRow("Character ID:", self.char_id)
        details_layout.addRow("Name:", self.char_name)
        details_layout.addRow("Title:", self.char_title)
        details_layout.addRow("Affiliation:", self.char_affiliation)
        details_layout.addRow("Description:", self.char_description)
        details_layout.addRow("Biography:", self.char_bio)
        
        details_group.setLayout(details_layout)
        right_layout.addWidget(details_group)
        
        # Portrait section
        portrait_group = QGroupBox("Character Portrait (Optional)")
        portrait_layout = QVBoxLayout()
        
        portrait_info = QLabel("For generic units, portrait can be left empty.")
        portrait_info.setWordWrap(True)
        portrait_info.setStyleSheet("color: #666; font-size: 10px;")
        portrait_layout.addWidget(portrait_info)
        
        portrait_file_layout = QHBoxLayout()
        self.char_portrait = QLineEdit()
        self.char_portrait.setPlaceholderText("No portrait assigned")
        self.char_portrait.setReadOnly(True)
        self.char_portrait.textChanged.connect(self.update_current_character)
        
        browse_portrait_btn = QPushButton("Browse...")
        browse_portrait_btn.clicked.connect(self.browse_portrait)
        clear_portrait_btn = QPushButton("Clear")
        clear_portrait_btn.clicked.connect(lambda: self.char_portrait.clear())
        
        portrait_file_layout.addWidget(self.char_portrait)
        portrait_file_layout.addWidget(browse_portrait_btn)
        portrait_file_layout.addWidget(clear_portrait_btn)
        portrait_layout.addLayout(portrait_file_layout)
        
        portrait_group.setLayout(portrait_layout)
        right_layout.addWidget(portrait_group)
        
        # Sprites section
        sprites_group = QGroupBox("Character Sprites (Optional)")
        sprites_layout = QVBoxLayout()
        
        sprites_info = QLabel("Add multiple sprites with custom labels (e.g., 'Idle', 'Attack', 'Promoted'). For generic units, sprites can be left empty.")
        sprites_info.setWordWrap(True)
        sprites_info.setStyleSheet("color: #666; font-size: 10px;")
        sprites_layout.addWidget(sprites_info)
        
        self.sprites_list = QListWidget()
        self.sprites_list.setMaximumHeight(150)
        sprites_layout.addWidget(self.sprites_list)
        
        sprites_btn_layout = QHBoxLayout()
        add_sprite_btn = QPushButton("Add Sprite...")
        add_sprite_btn.clicked.connect(self.add_sprite)
        remove_sprite_btn = QPushButton("Remove Selected")
        remove_sprite_btn.clicked.connect(self.remove_sprite)
        sprites_btn_layout.addWidget(add_sprite_btn)
        sprites_btn_layout.addWidget(remove_sprite_btn)
        sprites_layout.addLayout(sprites_btn_layout)
        
        sprites_group.setLayout(sprites_layout)
        right_layout.addWidget(sprites_group)
        
        right_layout.addStretch()
        
        layout.addWidget(scroll, 2)
        
        self._updating = False
        
    def add_character(self):
        """Add a new character"""
        character = {
            'id': generate_character_id(),  # Generate 8-digit ID
            'name': 'New Character',
            'title': '',
            'affiliation': 'Player',
            'description': '',
            'biography': '',
            'portrait': '',  # Optional
            'sprites': []  # List of {label, path} dicts
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
            self._updating = True
            
            char = self.characters[index]
            
            # Ensure character has new fields (for backwards compatibility)
            if 'id' not in char:
                char['id'] = generate_character_id()
            if 'portrait' not in char:
                char['portrait'] = ''
            if 'sprites' not in char:
                char['sprites'] = []
            
            self.char_id.setText(char['id'])
            self.char_name.setText(char['name'])
            self.char_title.setText(char['title'])
            self.char_affiliation.setCurrentText(char['affiliation'])
            self.char_description.setPlainText(char['description'])
            self.char_bio.setPlainText(char['biography'])
            self.char_portrait.setText(char['portrait'])
            
            # Load sprites list
            self.sprites_list.clear()
            for sprite in char.get('sprites', []):
                label = sprite.get('label', 'Sprite')
                path = sprite.get('path', '')
                self.sprites_list.addItem(f"{label}: {path}")
            
            self._updating = False
    
    def update_current_character(self):
        """Update current character with form data"""
        if self._updating:
            return
        
        index = self.character_list.currentRow()
        if 0 <= index < len(self.characters):
            char = self.characters[index]
            char['name'] = self.char_name.text()
            char['title'] = self.char_title.text()
            char['affiliation'] = self.char_affiliation.currentText()
            char['description'] = self.char_description.toPlainText()
            char['biography'] = self.char_bio.toPlainText()
            char['portrait'] = self.char_portrait.text()
            
            # Update list item display
            self.character_list.item(index).setText(char['name'])
    
    def browse_portrait(self):
        """Browse for portrait image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Character Portrait",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*.*)"
        )
        
        if file_path:
            self.char_portrait.setText(file_path)
    
    def add_sprite(self):
        """Add a sprite with custom label"""
        from PyQt6.QtWidgets import QInputDialog
        
        # Get sprite label
        label, ok = QInputDialog.getText(
            self,
            "Sprite Label",
            "Enter a label for this sprite (e.g., 'Idle', 'Attack', 'Promoted'):",
            QLineEdit.EchoMode.Normal,
            "Sprite"
        )
        
        if not ok or not label:
            return
        
        # Browse for sprite file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Sprite Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*.*)"
        )
        
        if file_path:
            index = self.character_list.currentRow()
            if 0 <= index < len(self.characters):
                char = self.characters[index]
                if 'sprites' not in char:
                    char['sprites'] = []
                
                char['sprites'].append({
                    'label': label,
                    'path': file_path
                })
                
                self.sprites_list.addItem(f"{label}: {file_path}")
    
    def remove_sprite(self):
        """Remove selected sprite"""
        row = self.sprites_list.currentRow()
        if row >= 0:
            index = self.character_list.currentRow()
            if 0 <= index < len(self.characters):
                char = self.characters[index]
                if 'sprites' in char and row < len(char['sprites']):
                    char['sprites'].pop(row)
                    self.sprites_list.takeItem(row)
            
    def get_data(self):
        """Get characters data"""
        return self.characters
        
    def load_data(self, characters):
        """Load characters data"""
        self.characters = characters
        self.character_list.clear()
        for char in characters:
            self.character_list.addItem(char['name'])


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
