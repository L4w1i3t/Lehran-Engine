"""
Gameplay Editor for Lehran Engine
Handles units, classes, weapons, items, and stats
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                              QListWidget, QGroupBox, QPushButton, QLabel,
                              QLineEdit, QTextEdit, QComboBox, QSpinBox,
                              QFormLayout, QCheckBox, QTableWidget, 
                              QTableWidgetItem, QHeaderView, QScrollArea)
from PyQt6.QtCore import Qt


class GameplayEditor(QWidget):
    """Editor for gameplay elements"""
    
    def __init__(self, story_editor=None):
        super().__init__()
        self.story_editor = story_editor
        self.init_ui()
        
    def init_ui(self):
        """Initialize the gameplay editor UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create tab widget for different gameplay aspects
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Create all widgets first (before passing as parameters)
        self.classes_widget = ClassesWidget()
        self.weapons_widget = WeaponsWidget()
        self.items_widget = ItemsWidget()
        self.stats_widget = StatsWidget()
        
        # Now create units widget with references to other widgets
        self.units_widget = UnitsWidget(self.classes_widget, self.weapons_widget, self.items_widget, self.story_editor)
        
        # Add tabs
        tabs.addTab(self.classes_widget, "Classes")
        tabs.addTab(self.units_widget, "Units")
        tabs.addTab(self.weapons_widget, "Weapons")
        tabs.addTab(self.items_widget, "Items")
        tabs.addTab(self.stats_widget, "Stats Config")
        
        # Connect class changes to update unit class dropdown
        self.classes_widget.class_list.model().rowsInserted.connect(self.update_unit_classes)
        self.classes_widget.class_list.model().rowsRemoved.connect(self.update_unit_classes)
        self.classes_widget.class_list.model().dataChanged.connect(self.update_unit_classes)
        
        # Connect weapon/item changes to update unit inventory dropdowns
        self.weapons_widget.weapon_list.model().rowsInserted.connect(self.update_unit_inventory)
        self.weapons_widget.weapon_list.model().rowsRemoved.connect(self.update_unit_inventory)
        self.weapons_widget.weapon_list.model().dataChanged.connect(self.update_unit_inventory)
        
        # Connect item changes to update unit inventory dropdowns
        self.items_widget.item_list.model().rowsInserted.connect(self.update_unit_inventory)
        self.items_widget.item_list.model().rowsRemoved.connect(self.update_unit_inventory)
        self.items_widget.item_list.model().dataChanged.connect(self.update_unit_inventory)
        
        # Connect character changes to update unit character dropdown
        if self.story_editor:
            self.story_editor.characters_widget.character_list.model().rowsInserted.connect(self.update_unit_characters)
            self.story_editor.characters_widget.character_list.model().rowsRemoved.connect(self.update_unit_characters)
            self.story_editor.characters_widget.character_list.model().dataChanged.connect(self.update_unit_characters)
        
    def update_unit_classes(self):
        """Update the unit class dropdown when classes change"""
        self.units_widget.refresh_class_list()
    
    def update_unit_inventory(self):
        """Update the unit inventory dropdowns when weapons/items change"""
        self.units_widget.refresh_inventory_items()
    
    def update_unit_characters(self):
        """Update the unit character dropdown when characters change"""
        self.units_widget.refresh_character_list()
        
    def get_data(self):
        """Get all gameplay data"""
        return {
            'classes': self.classes_widget.get_data(),
            'units': self.units_widget.get_data(),
            'weapons': self.weapons_widget.get_data(),
            'items': self.items_widget.get_data(),
            'stats': self.stats_widget.get_data()
        }
        
    def load_data(self, data):
        """Load gameplay data"""
        # Block signals during load to prevent triggering change detection
        self.classes_widget.class_list.blockSignals(True)
        self.units_widget.unit_list.blockSignals(True)
        self.weapons_widget.weapon_list.blockSignals(True)
        self.items_widget.item_list.blockSignals(True)
        
        try:
            self.classes_widget.load_data(data.get('classes', []))
            self.units_widget.load_data(data.get('units', []))
            self.weapons_widget.load_data(data.get('weapons', []))
            self.items_widget.load_data(data.get('items', []))
            self.stats_widget.load_data(data.get('stats', {}))
        finally:
            # Always restore signals
            self.classes_widget.class_list.blockSignals(False)
            self.units_widget.unit_list.blockSignals(False)
            self.weapons_widget.weapon_list.blockSignals(False)
            self.items_widget.item_list.blockSignals(False)


class ClassesWidget(QWidget):
    """Widget for managing character classes"""
    
    def __init__(self):
        super().__init__()
        self.classes = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the classes UI"""
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Left side - class list
        left_layout = QVBoxLayout()
        
        left_layout.addWidget(QLabel("Classes:"))
        self.class_list = QListWidget()
        self.class_list.currentRowChanged.connect(self.on_class_selected)
        self.class_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.class_list.model().rowsMoved.connect(self.on_class_reordered)
        left_layout.addWidget(self.class_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Class")
        add_btn.clicked.connect(self.add_class)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_class)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        left_layout.addLayout(btn_layout)
        
        layout.addLayout(left_layout, 1)
        
        # Right side - class details (with scroll area)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        
        details_group = QGroupBox("Class Details")
        details_layout = QFormLayout()
        
        self.class_name = QLineEdit()
        self.class_type = QComboBox()
        self.class_type.addItems(["Infantry", "Cavalry", "Armor", "Flying", "Monster", "Special"])
        self.class_description = QTextEdit()
        self.class_description.setMaximumHeight(80)
        
        details_layout.addRow("Class Name:", self.class_name)
        details_layout.addRow("Class Type:", self.class_type)
        details_layout.addRow("Description:", self.class_description)
        
        details_group.setLayout(details_layout)
        right_layout.addWidget(details_group)
        
        # Base stats
        stats_group = QGroupBox("Class Stat Modifiers")
        stats_layout = QFormLayout()
        
        stats_layout.addWidget(QLabel("Bonuses added to character's base stats:"))
        
        self.stat_hp = QSpinBox()
        self.stat_str = QSpinBox()
        self.stat_mag = QSpinBox()
        self.stat_skl = QSpinBox()
        self.stat_spd = QSpinBox()
        self.stat_lck = QSpinBox()
        self.stat_def = QSpinBox()
        self.stat_res = QSpinBox()
        
        for spin in [self.stat_hp, self.stat_str, self.stat_mag, self.stat_skl,
                     self.stat_spd, self.stat_lck, self.stat_def, self.stat_res]:
            spin.setRange(-30, 30)  # Allow negative modifiers
            spin.setValue(0)
            
        stats_layout.addRow("HP Bonus:", self.stat_hp)
        stats_layout.addRow("STR Bonus:", self.stat_str)
        stats_layout.addRow("MAG Bonus:", self.stat_mag)
        stats_layout.addRow("SKL Bonus:", self.stat_skl)
        stats_layout.addRow("SPD Bonus:", self.stat_spd)
        stats_layout.addRow("LCK Bonus:", self.stat_lck)
        stats_layout.addRow("DEF Bonus:", self.stat_def)
        stats_layout.addRow("RES Bonus:", self.stat_res)
        
        stats_group.setLayout(stats_layout)
        right_layout.addWidget(stats_group)
        
        # Growth rate modifiers
        growth_group = QGroupBox("Class Growth Rate Modifiers")
        growth_layout = QFormLayout()
        
        growth_layout.addWidget(QLabel("Percentage bonuses to character's growth rates:"))
        
        self.growth_hp = QSpinBox()
        self.growth_str = QSpinBox()
        self.growth_mag = QSpinBox()
        self.growth_skl = QSpinBox()
        self.growth_spd = QSpinBox()
        self.growth_lck = QSpinBox()
        self.growth_def = QSpinBox()
        self.growth_res = QSpinBox()
        
        for spin in [self.growth_hp, self.growth_str, self.growth_mag, self.growth_skl,
                     self.growth_spd, self.growth_lck, self.growth_def, self.growth_res]:
            spin.setRange(-100, 100)  # Allow negative modifiers
            spin.setValue(0)
            spin.setSuffix("%")
            
        growth_layout.addRow("HP Growth:", self.growth_hp)
        growth_layout.addRow("STR Growth:", self.growth_str)
        growth_layout.addRow("MAG Growth:", self.growth_mag)
        growth_layout.addRow("SKL Growth:", self.growth_skl)
        growth_layout.addRow("SPD Growth:", self.growth_spd)
        growth_layout.addRow("LCK Growth:", self.growth_lck)
        growth_layout.addRow("DEF Growth:", self.growth_def)
        growth_layout.addRow("RES Growth:", self.growth_res)
        
        growth_group.setLayout(growth_layout)
        right_layout.addWidget(growth_group)
        
        # Weapon proficiencies
        weapon_group = QGroupBox("Weapon Proficiencies")
        weapon_layout = QVBoxLayout()
        
        weapon_layout.addWidget(QLabel("Usable weapon types (max 4):"))
        
        self.weapon_checks = {}
        weapon_types = ["Sword", "Lance", "Axe", "Bow", "Tome", "Staff", "Special"]
        
        for weapon_type in weapon_types:
            checkbox = QCheckBox(weapon_type)
            checkbox.stateChanged.connect(self.on_weapon_check_changed)
            self.weapon_checks[weapon_type] = checkbox
            weapon_layout.addWidget(checkbox)
        
        weapon_group.setLayout(weapon_layout)
        right_layout.addWidget(weapon_group)
        
        # Movement
        movement_group = QGroupBox("Movement")
        movement_layout = QFormLayout()
        
        self.movement = QSpinBox()
        self.movement.setMaximum(20)
        movement_layout.addRow("Movement:", self.movement)
        
        movement_group.setLayout(movement_layout)
        right_layout.addWidget(movement_group)
        
        right_layout.addStretch()
        
        scroll.setWidget(right_widget)
        layout.addWidget(scroll, 2)
        
    def on_weapon_check_changed(self):
        """Limit weapon selections to 4"""
        checked_count = sum(1 for cb in self.weapon_checks.values() if cb.isChecked())
        
        if checked_count >= 4:
            # Disable unchecked boxes
            for cb in self.weapon_checks.values():
                if not cb.isChecked():
                    cb.setEnabled(False)
        else:
            # Enable all boxes
            for cb in self.weapon_checks.values():
                cb.setEnabled(True)
        
    def add_class(self):
        """Add a new class"""
        class_data = {
            'name': 'New Class',
            'type': 'Infantry',
            'description': '',
            'stat_modifiers': {'hp': 0, 'str': 0, 'mag': 0, 'skl': 0, 'spd': 0, 'lck': 0, 'def': 0, 'res': 0},
            'growth_modifiers': {'hp': 0, 'str': 0, 'mag': 0, 'skl': 0, 'spd': 0, 'lck': 0, 'def': 0, 'res': 0},
            'weapon_types': [],
            'movement': 5
        }
        self.classes.append(class_data)
        self.class_list.addItem(class_data['name'])
        self.class_list.setCurrentRow(len(self.classes) - 1)
        
    def remove_class(self):
        """Remove selected class"""
        row = self.class_list.currentRow()
        if row >= 0:
            self.classes.pop(row)
            self.class_list.takeItem(row)
            
    def move_class_up(self):
        """Move selected class up in the list"""
        row = self.class_list.currentRow()
        if row > 0:
            # Save current class data
            self.update_class_data(row)
            # Swap in data list
            self.classes[row], self.classes[row - 1] = self.classes[row - 1], self.classes[row]
            # Update list widget with correct names
            self.class_list.item(row).setText(self.classes[row]['name'])
            self.class_list.item(row - 1).setText(self.classes[row - 1]['name'])
            # Move selection
            self.class_list.setCurrentRow(row - 1)
            
    def move_class_down(self):
        """Move selected class down in the list"""
        row = self.class_list.currentRow()
        if row >= 0 and row < len(self.classes) - 1:
            # Save current class data
            self.update_class_data(row)
            # Swap in data list
            self.classes[row], self.classes[row + 1] = self.classes[row + 1], self.classes[row]
            # Update list widget with correct names
            self.class_list.item(row).setText(self.classes[row]['name'])
            self.class_list.item(row + 1).setText(self.classes[row + 1]['name'])
            # Move selection
            self.class_list.setCurrentRow(row + 1)
            
    def on_class_reordered(self):
        """Handle drag-and-drop reordering"""
        # Rebuild classes list based on current list widget order
        new_order = []
        for i in range(self.class_list.count()):
            class_name = self.class_list.item(i).text()
            # Find the class with this name
            for cls in self.classes:
                if cls['name'] == class_name:
                    new_order.append(cls)
                    break
        self.classes = new_order
            
    def on_class_selected(self, index):
        """Handle class selection"""
        # Save the previously selected class first
        if hasattr(self, '_previous_class_index') and 0 <= self._previous_class_index < len(self.classes):
            self.update_class_data(self._previous_class_index)
        
        if 0 <= index < len(self.classes):
            self._previous_class_index = index
            
            # Disconnect any existing signals to prevent duplicate connections
            try:
                self.class_name.textChanged.disconnect()
                self.class_type.currentTextChanged.disconnect()
                self.class_description.textChanged.disconnect()
                self.stat_hp.valueChanged.disconnect()
                self.stat_str.valueChanged.disconnect()
                self.stat_mag.valueChanged.disconnect()
                self.stat_skl.valueChanged.disconnect()
                self.stat_spd.valueChanged.disconnect()
                self.stat_lck.valueChanged.disconnect()
                self.stat_def.valueChanged.disconnect()
                self.stat_res.valueChanged.disconnect()
                self.growth_hp.valueChanged.disconnect()
                self.growth_str.valueChanged.disconnect()
                self.growth_mag.valueChanged.disconnect()
                self.growth_skl.valueChanged.disconnect()
                self.growth_spd.valueChanged.disconnect()
                self.growth_lck.valueChanged.disconnect()
                self.growth_def.valueChanged.disconnect()
                self.growth_res.valueChanged.disconnect()
                self.movement.valueChanged.disconnect()
                for cb in self.weapon_checks.values():
                    cb.stateChanged.disconnect()
            except:
                pass
            
            cls = self.classes[index]
            self.class_name.setText(cls['name'])
            self.class_type.setCurrentText(cls['type'])
            self.class_description.setPlainText(cls['description'])
            
            # Handle both old 'base_stats' and new 'stat_modifiers' format
            stats = cls.get('stat_modifiers', cls.get('base_stats', {}))
            self.stat_hp.setValue(stats.get('hp', 0))
            self.stat_str.setValue(stats.get('str', 0))
            self.stat_mag.setValue(stats.get('mag', 0))
            self.stat_skl.setValue(stats.get('skl', 0))
            self.stat_spd.setValue(stats.get('spd', 0))
            self.stat_lck.setValue(stats.get('lck', 0))
            self.stat_def.setValue(stats.get('def', 0))
            self.stat_res.setValue(stats.get('res', 0))
            
            # Growth modifiers
            growths = cls.get('growth_modifiers', {})
            self.growth_hp.setValue(growths.get('hp', 0))
            self.growth_str.setValue(growths.get('str', 0))
            self.growth_mag.setValue(growths.get('mag', 0))
            self.growth_skl.setValue(growths.get('skl', 0))
            self.growth_spd.setValue(growths.get('spd', 0))
            self.growth_lck.setValue(growths.get('lck', 0))
            self.growth_def.setValue(growths.get('def', 0))
            self.growth_res.setValue(growths.get('res', 0))
            
            # Weapon types
            weapon_types = cls.get('weapon_types', [])
            for weapon_type, checkbox in self.weapon_checks.items():
                checkbox.setChecked(weapon_type in weapon_types)
            self.on_weapon_check_changed()  # Update enabled state
            
            self.movement.setValue(cls.get('movement', 5))
            
            # Connect signals to update data
            self.class_name.textChanged.connect(lambda text: self.update_class_data(index))
            self.class_type.currentTextChanged.connect(lambda text: self.update_class_data(index))
            self.class_description.textChanged.connect(lambda: self.update_class_data(index))
            self.stat_hp.valueChanged.connect(lambda val: self.update_class_data(index))
            self.stat_str.valueChanged.connect(lambda val: self.update_class_data(index))
            self.stat_mag.valueChanged.connect(lambda val: self.update_class_data(index))
            self.stat_skl.valueChanged.connect(lambda val: self.update_class_data(index))
            self.stat_spd.valueChanged.connect(lambda val: self.update_class_data(index))
            self.stat_lck.valueChanged.connect(lambda val: self.update_class_data(index))
            self.stat_def.valueChanged.connect(lambda val: self.update_class_data(index))
            self.stat_res.valueChanged.connect(lambda val: self.update_class_data(index))
            self.growth_hp.valueChanged.connect(lambda val: self.update_class_data(index))
            self.growth_str.valueChanged.connect(lambda val: self.update_class_data(index))
            self.growth_mag.valueChanged.connect(lambda val: self.update_class_data(index))
            self.growth_skl.valueChanged.connect(lambda val: self.update_class_data(index))
            self.growth_spd.valueChanged.connect(lambda val: self.update_class_data(index))
            self.growth_lck.valueChanged.connect(lambda val: self.update_class_data(index))
            self.growth_def.valueChanged.connect(lambda val: self.update_class_data(index))
            self.growth_res.valueChanged.connect(lambda val: self.update_class_data(index))
            self.movement.valueChanged.connect(lambda val: self.update_class_data(index))
            for cb in self.weapon_checks.values():
                cb.stateChanged.connect(lambda state: self.update_class_data(index))
            
    def update_class_data(self, index):
        """Update all class data from UI fields"""
        if 0 <= index < len(self.classes):
            cls = self.classes[index]
            cls['name'] = self.class_name.text()
            cls['type'] = self.class_type.currentText()
            cls['description'] = self.class_description.toPlainText()
            cls['stat_modifiers'] = {
                'hp': self.stat_hp.value(),
                'str': self.stat_str.value(),
                'mag': self.stat_mag.value(),
                'skl': self.stat_skl.value(),
                'spd': self.stat_spd.value(),
                'lck': self.stat_lck.value(),
                'def': self.stat_def.value(),
                'res': self.stat_res.value()
            }
            cls['growth_modifiers'] = {
                'hp': self.growth_hp.value(),
                'str': self.growth_str.value(),
                'mag': self.growth_mag.value(),
                'skl': self.growth_skl.value(),
                'spd': self.growth_spd.value(),
                'lck': self.growth_lck.value(),
                'def': self.growth_def.value(),
                'res': self.growth_res.value()
            }
            cls['weapon_types'] = [weapon_type for weapon_type, cb in self.weapon_checks.items() if cb.isChecked()]
            cls['movement'] = self.movement.value()
            # Update the list item text
            self.class_list.item(index).setText(cls['name'])
            
    def get_data(self):
        """Get classes data"""
        # Save the currently selected class before returning data
        current_index = self.class_list.currentRow()
        if 0 <= current_index < len(self.classes):
            self.update_class_data(current_index)
        return self.classes
        
    def load_data(self, classes):
        """Load classes data"""
        self.classes = classes
        self.class_list.clear()
        for cls in classes:
            self.class_list.addItem(cls['name'])


class UnitsWidget(QWidget):
    """Widget for managing units"""
    
    def __init__(self, classes_widget, weapons_widget, items_widget, story_editor=None):
        super().__init__()
        self.classes_widget = classes_widget
        self.weapons_widget = weapons_widget
        self.items_widget = items_widget
        self.story_editor = story_editor
        self.units = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the units UI"""
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Left side - unit list
        left_layout = QVBoxLayout()
        
        left_layout.addWidget(QLabel("Units:"))
        self.unit_list = QListWidget()
        self.unit_list.currentRowChanged.connect(self.on_unit_selected)
        self.unit_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.unit_list.model().rowsMoved.connect(self.on_unit_reordered)
        left_layout.addWidget(self.unit_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Unit")
        add_btn.clicked.connect(self.add_unit)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_unit)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        left_layout.addLayout(btn_layout)
        
        layout.addLayout(left_layout, 1)
        
        # Right side - unit details (with scroll area)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        
        # Basic info
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout()
        
        self.unit_name = QLineEdit()
        self.unit_class = QComboBox()
        self.unit_class.setEditable(False)  # Only allow selection from defined classes
        self.unit_level = QSpinBox()
        self.unit_level.setRange(1, 30)
        self.unit_level.setValue(1)
        
        # Character link (optional)
        self.unit_character = QComboBox()
        self.unit_character.setEditable(False)
        self.refresh_character_list()
        
        # Populate class list from classes widget
        self.refresh_class_list()
        
        basic_layout.addRow("Name:", self.unit_name)
        basic_layout.addRow("Class:", self.unit_class)
        basic_layout.addRow("Level:", self.unit_level)
        
        # Add character link row with info label
        char_link_layout = QVBoxLayout()
        char_link_layout.addWidget(self.unit_character)
        char_info = QLabel("Link this unit to a character for tracking story flags (death, recruitment, etc.)")
        char_info.setWordWrap(True)
        char_info.setStyleSheet("color: #666; font-size: 10px;")
        char_link_layout.addWidget(char_info)
        basic_layout.addRow("Linked Character:", char_link_layout)
        
        basic_group.setLayout(basic_layout)
        right_layout.addWidget(basic_group)
        
        # Faction and special flags
        faction_group = QGroupBox("Faction & Flags")
        faction_layout = QFormLayout()
        
        self.unit_faction = QComboBox()
        self.unit_faction.addItems(["Player", "Enemy", "Ally", "NPC", "Other"])
        
        self.unit_is_lord = QCheckBox("Lord (Game Over if defeated)")
        self.unit_is_boss = QCheckBox("Boss")
        self.unit_recruitable = QCheckBox("Recruitable")
        
        faction_layout.addRow("Faction:", self.unit_faction)
        faction_layout.addRow("", self.unit_is_lord)
        faction_layout.addRow("", self.unit_is_boss)
        faction_layout.addRow("", self.unit_recruitable)
        
        faction_group.setLayout(faction_layout)
        right_layout.addWidget(faction_group)
        
        # Stats
        stats_group = QGroupBox("Character Base Stats")
        stats_layout = QFormLayout()
        
        stats_layout.addWidget(QLabel("Personal stats (before class modifiers):"))
        
        self.unit_hp = QSpinBox()
        self.unit_str = QSpinBox()
        self.unit_mag = QSpinBox()
        self.unit_skl = QSpinBox()
        self.unit_spd = QSpinBox()
        self.unit_lck = QSpinBox()
        self.unit_def = QSpinBox()
        self.unit_res = QSpinBox()
        
        for spin in [self.unit_hp, self.unit_str, self.unit_mag, self.unit_skl,
                     self.unit_spd, self.unit_lck, self.unit_def, self.unit_res]:
            spin.setMaximum(99)
            
        stats_layout.addRow("HP:", self.unit_hp)
        stats_layout.addRow("STR:", self.unit_str)
        stats_layout.addRow("MAG:", self.unit_mag)
        stats_layout.addRow("SKL:", self.unit_skl)
        stats_layout.addRow("SPD:", self.unit_spd)
        stats_layout.addRow("LCK:", self.unit_lck)
        stats_layout.addRow("DEF:", self.unit_def)
        stats_layout.addRow("RES:", self.unit_res)
        
        stats_group.setLayout(stats_layout)
        right_layout.addWidget(stats_group)
        
        # Growth rates
        growth_group = QGroupBox("Character Growth Rates")
        growth_layout = QFormLayout()
        
        growth_layout.addWidget(QLabel("Personal growth rates (before class modifiers):"))
        
        self.unit_growth_hp = QSpinBox()
        self.unit_growth_str = QSpinBox()
        self.unit_growth_mag = QSpinBox()
        self.unit_growth_skl = QSpinBox()
        self.unit_growth_spd = QSpinBox()
        self.unit_growth_lck = QSpinBox()
        self.unit_growth_def = QSpinBox()
        self.unit_growth_res = QSpinBox()
        
        for spin in [self.unit_growth_hp, self.unit_growth_str, self.unit_growth_mag, self.unit_growth_skl,
                     self.unit_growth_spd, self.unit_growth_lck, self.unit_growth_def, self.unit_growth_res]:
            spin.setRange(0, 255)  # Fire Emblem growth rate range
            spin.setSuffix("%")
            
        growth_layout.addRow("HP Growth:", self.unit_growth_hp)
        growth_layout.addRow("STR Growth:", self.unit_growth_str)
        growth_layout.addRow("MAG Growth:", self.unit_growth_mag)
        growth_layout.addRow("SKL Growth:", self.unit_growth_skl)
        growth_layout.addRow("SPD Growth:", self.unit_growth_spd)
        growth_layout.addRow("LCK Growth:", self.unit_growth_lck)
        growth_layout.addRow("DEF Growth:", self.unit_growth_def)
        growth_layout.addRow("RES Growth:", self.unit_growth_res)
        
        growth_group.setLayout(growth_layout)
        right_layout.addWidget(growth_group)
        
        # Inventory (up to 5 items)
        inventory_group = QGroupBox("Starting Inventory")
        inventory_layout = QVBoxLayout()
        
        inventory_layout.addWidget(QLabel("Starting items (max 5):"))
        
        self.inventory_items = []
        for i in range(5):
            item_layout = QHBoxLayout()
            
            slot_label = QLabel(f"Slot {i+1}:")
            slot_label.setMinimumWidth(50)
            
            item_combo = QComboBox()
            item_combo.setEditable(False)  # Only allow selection from list
            item_combo.addItem("(Empty)")
            
            item_layout.addWidget(slot_label)
            item_layout.addWidget(item_combo)
            
            inventory_layout.addLayout(item_layout)
            self.inventory_items.append(item_combo)
        
        # Populate inventory items from weapons and items
        self.refresh_inventory_items()
        
        inventory_group.setLayout(inventory_layout)
        right_layout.addWidget(inventory_group)
        
        right_layout.addStretch()
        
        scroll.setWidget(right_widget)
        layout.addWidget(scroll, 2)
        
    def add_unit(self):
        """Add a new unit"""
        unit = {
            'name': 'New Unit',
            'class': 'Soldier',
            'level': 1,
            'character_id': '',  # Link to character by ID
            'faction': 'Player',
            'is_lord': False,
            'is_boss': False,
            'recruitable': False,
            'stats': {
                'hp': 20,
                'str': 5,
                'mag': 0,
                'skl': 5,
                'spd': 5,
                'lck': 0,
                'def': 5,
                'res': 0
            },
            'growths': {
                'hp': 50,
                'str': 40,
                'mag': 0,
                'skl': 40,
                'spd': 40,
                'lck': 30,
                'def': 30,
                'res': 20
            },
            'inventory': []
        }
        self.units.append(unit)
        self.unit_list.addItem(f"{unit['name']} ({unit['faction']})")
        self.unit_list.setCurrentRow(len(self.units) - 1)
        
    def remove_unit(self):
        """Remove selected unit"""
        row = self.unit_list.currentRow()
        if row >= 0:
            self.units.pop(row)
            self.unit_list.takeItem(row)
            
    def move_unit_up(self):
        """Move selected unit up in the list"""
        row = self.unit_list.currentRow()
        if row > 0:
            # Save current unit data
            self.update_unit_data(row)
            # Swap in data list
            self.units[row], self.units[row - 1] = self.units[row - 1], self.units[row]
            # Update list widget with correct display text
            faction_emoji = {"Player": "🔵", "Enemy": "🔴", "Ally": "🟢", "NPC": "⚪", "Other": "⚫"}.get(self.units[row].get('faction', 'Other'), '⚪')
            self.unit_list.item(row).setText(f"{self.units[row]['name']} - {self.units[row].get('class', 'No Class')} {faction_emoji}")
            faction_emoji = {"Player": "🔵", "Enemy": "🔴", "Ally": "🟢", "NPC": "⚪", "Other": "⚫"}.get(self.units[row - 1].get('faction', 'Other'), '⚪')
            self.unit_list.item(row - 1).setText(f"{self.units[row - 1]['name']} - {self.units[row - 1].get('class', 'No Class')} {faction_emoji}")
            # Move selection
            self.unit_list.setCurrentRow(row - 1)
            
    def move_unit_down(self):
        """Move selected unit down in the list"""
        row = self.unit_list.currentRow()
        if row >= 0 and row < len(self.units) - 1:
            # Save current unit data
            self.update_unit_data(row)
            # Swap in data list
            self.units[row], self.units[row + 1] = self.units[row + 1], self.units[row]
            # Update list widget with correct display text
            faction_emoji = {"Player": "🔵", "Enemy": "🔴", "Ally": "🟢", "NPC": "⚪", "Other": "⚫"}.get(self.units[row].get('faction', 'Other'), '⚪')
            self.unit_list.item(row).setText(f"{self.units[row]['name']} - {self.units[row].get('class', 'No Class')} {faction_emoji}")
            faction_emoji = {"Player": "🔵", "Enemy": "🔴", "Ally": "🟢", "NPC": "⚪", "Other": "⚫"}.get(self.units[row + 1].get('faction', 'Other'), '⚪')
            self.unit_list.item(row + 1).setText(f"{self.units[row + 1]['name']} - {self.units[row + 1].get('class', 'No Class')} {faction_emoji}")
            # Move selection
            self.unit_list.setCurrentRow(row + 1)
            
    def on_unit_reordered(self):
        """Handle drag-and-drop reordering"""
        # Rebuild units list based on current list widget order
        new_order = []
        for i in range(self.unit_list.count()):
            unit_display = self.unit_list.item(i).text()
            unit_name = unit_display.split(' - ')[0] if ' - ' in unit_display else unit_display
            # Find the unit with this name
            for unit in self.units:
                if unit['name'] == unit_name:
                    new_order.append(unit)
                    break
        self.units = new_order
            
    def on_unit_selected(self, index):
        """Handle unit selection"""
        # Save the previously selected unit first
        if hasattr(self, '_previous_unit_index') and 0 <= self._previous_unit_index < len(self.units):
            self.update_unit_data(self._previous_unit_index)
        
        if 0 <= index < len(self.units):
            self._previous_unit_index = index
            
            # Disconnect any existing signals to prevent duplicate connections
            try:
                self.unit_name.textChanged.disconnect()
                self.unit_class.currentTextChanged.disconnect()
                self.unit_level.valueChanged.disconnect()
                self.unit_character.currentTextChanged.disconnect()
                self.unit_faction.currentTextChanged.disconnect()
                self.unit_is_lord.stateChanged.disconnect()
                self.unit_is_boss.stateChanged.disconnect()
                self.unit_recruitable.stateChanged.disconnect()
                self.unit_hp.valueChanged.disconnect()
                self.unit_str.valueChanged.disconnect()
                self.unit_mag.valueChanged.disconnect()
                self.unit_skl.valueChanged.disconnect()
                self.unit_spd.valueChanged.disconnect()
                self.unit_lck.valueChanged.disconnect()
                self.unit_def.valueChanged.disconnect()
                self.unit_res.valueChanged.disconnect()
                self.unit_growth_hp.valueChanged.disconnect()
                self.unit_growth_str.valueChanged.disconnect()
                self.unit_growth_mag.valueChanged.disconnect()
                self.unit_growth_skl.valueChanged.disconnect()
                self.unit_growth_spd.valueChanged.disconnect()
                self.unit_growth_lck.valueChanged.disconnect()
                self.unit_growth_def.valueChanged.disconnect()
                self.unit_growth_res.valueChanged.disconnect()
                for item_combo in self.inventory_items:
                    item_combo.currentTextChanged.disconnect()
            except:
                pass
            
            unit = self.units[index]
            
            # Basic info
            self.unit_name.setText(unit['name'])
            self.unit_class.setCurrentText(unit.get('class', 'Soldier'))
            self.unit_level.setValue(unit.get('level', 1))
            
            # Set character link (backward compatible)
            character_id = unit.get('character_id', '')
            if character_id:
                # Find character by ID and set combo box
                index = self.unit_character.findData(character_id)
                if index >= 0:
                    self.unit_character.setCurrentIndex(index)
                else:
                    self.unit_character.setCurrentIndex(0)  # (None)
            else:
                self.unit_character.setCurrentIndex(0)  # (None)
            
            # Faction and flags
            self.unit_faction.setCurrentText(unit.get('faction', 'Player'))
            self.unit_is_lord.setChecked(unit.get('is_lord', False))
            self.unit_is_boss.setChecked(unit.get('is_boss', False))
            self.unit_recruitable.setChecked(unit.get('recruitable', False))
            
            # Stats
            stats = unit.get('stats', {})
            self.unit_hp.setValue(stats.get('hp', 20))
            self.unit_str.setValue(stats.get('str', 5))
            self.unit_mag.setValue(stats.get('mag', 0))
            self.unit_skl.setValue(stats.get('skl', 5))
            self.unit_spd.setValue(stats.get('spd', 5))
            self.unit_lck.setValue(stats.get('lck', 0))
            self.unit_def.setValue(stats.get('def', 5))
            self.unit_res.setValue(stats.get('res', 0))
            
            # Growth rates
            growths = unit.get('growths', {})
            self.unit_growth_hp.setValue(growths.get('hp', 50))
            self.unit_growth_str.setValue(growths.get('str', 40))
            self.unit_growth_mag.setValue(growths.get('mag', 0))
            self.unit_growth_skl.setValue(growths.get('skl', 40))
            self.unit_growth_spd.setValue(growths.get('spd', 40))
            self.unit_growth_lck.setValue(growths.get('lck', 30))
            self.unit_growth_def.setValue(growths.get('def', 30))
            self.unit_growth_res.setValue(growths.get('res', 20))
            
            # Inventory
            inventory = unit.get('inventory', unit.get('items', []))  # Support old format
            for i, item_combo in enumerate(self.inventory_items):
                if i < len(inventory) and inventory[i]:
                    item_combo.setCurrentText(inventory[i])
                else:
                    item_combo.setCurrentText("(Empty)")
            
            # Connect signals to update data
            self.unit_name.textChanged.connect(lambda text: self.update_unit_data(index))
            self.unit_class.currentTextChanged.connect(lambda text: self.update_unit_data(index))
            self.unit_level.valueChanged.connect(lambda val: self.update_unit_data(index))
            self.unit_character.currentTextChanged.connect(lambda text: self.update_unit_data(index))
            self.unit_faction.currentTextChanged.connect(lambda text: self.update_unit_faction(index))
            self.unit_is_lord.stateChanged.connect(lambda state: self.update_unit_data(index))
            self.unit_is_boss.stateChanged.connect(lambda state: self.update_unit_data(index))
            self.unit_recruitable.stateChanged.connect(lambda state: self.update_unit_data(index))
            self.unit_hp.valueChanged.connect(lambda val: self.update_unit_data(index))
            self.unit_str.valueChanged.connect(lambda val: self.update_unit_data(index))
            self.unit_mag.valueChanged.connect(lambda val: self.update_unit_data(index))
            self.unit_skl.valueChanged.connect(lambda val: self.update_unit_data(index))
            self.unit_spd.valueChanged.connect(lambda val: self.update_unit_data(index))
            self.unit_lck.valueChanged.connect(lambda val: self.update_unit_data(index))
            self.unit_def.valueChanged.connect(lambda val: self.update_unit_data(index))
            self.unit_res.valueChanged.connect(lambda val: self.update_unit_data(index))
            self.unit_growth_hp.valueChanged.connect(lambda val: self.update_unit_data(index))
            self.unit_growth_str.valueChanged.connect(lambda val: self.update_unit_data(index))
            self.unit_growth_mag.valueChanged.connect(lambda val: self.update_unit_data(index))
            self.unit_growth_skl.valueChanged.connect(lambda val: self.update_unit_data(index))
            self.unit_growth_spd.valueChanged.connect(lambda val: self.update_unit_data(index))
            self.unit_growth_lck.valueChanged.connect(lambda val: self.update_unit_data(index))
            self.unit_growth_def.valueChanged.connect(lambda val: self.update_unit_data(index))
            self.unit_growth_res.valueChanged.connect(lambda val: self.update_unit_data(index))
            for item_combo in self.inventory_items:
                item_combo.currentTextChanged.connect(lambda text: self.update_unit_data(index))
            
    def update_unit_data(self, index):
        """Update all unit data from UI fields"""
        if 0 <= index < len(self.units):
            unit = self.units[index]
            unit['name'] = self.unit_name.text()
            unit['class'] = self.unit_class.currentText()
            unit['level'] = self.unit_level.value()
            
            # Save character ID link
            character_id = self.unit_character.currentData()
            unit['character_id'] = character_id if character_id else ''
            
            unit['faction'] = self.unit_faction.currentText()
            unit['is_lord'] = self.unit_is_lord.isChecked()
            unit['is_boss'] = self.unit_is_boss.isChecked()
            unit['recruitable'] = self.unit_recruitable.isChecked()
            unit['stats'] = {
                'hp': self.unit_hp.value(),
                'str': self.unit_str.value(),
                'mag': self.unit_mag.value(),
                'skl': self.unit_skl.value(),
                'spd': self.unit_spd.value(),
                'lck': self.unit_lck.value(),
                'def': self.unit_def.value(),
                'res': self.unit_res.value()
            }
            unit['growths'] = {
                'hp': self.unit_growth_hp.value(),
                'str': self.unit_growth_str.value(),
                'mag': self.unit_growth_mag.value(),
                'skl': self.unit_growth_skl.value(),
                'spd': self.unit_growth_spd.value(),
                'lck': self.unit_growth_lck.value(),
                'def': self.unit_growth_def.value(),
                'res': self.unit_growth_res.value()
            }
            
            # Inventory - only save non-empty slots
            inventory = []
            for item_combo in self.inventory_items:
                item_name = item_combo.currentText()
                if item_name and item_name != "(Empty)":
                    inventory.append(item_name)
            unit['inventory'] = inventory
            
            # Update the list item text to reflect changes
            self.unit_list.item(index).setText(f"{unit['name']} ({unit['faction']})")
    
    def update_unit_field(self, index, field, value):
        """Update a specific field in the unit data"""
        if 0 <= index < len(self.units):
            self.units[index][field] = value
            
    def update_unit_faction(self, index):
        """Update faction and refresh list display"""
        if 0 <= index < len(self.units):
            self.units[index]['faction'] = self.unit_faction.currentText()
            unit = self.units[index]
            self.unit_list.item(index).setText(f"{unit['name']} ({unit['faction']})")
        
    def get_data(self):
        """Save current selections before returning data"""
        current_index = self.unit_list.currentRow()
        if 0 <= current_index < len(self.units):
            self.update_unit_data(current_index)
            
        return self.units
        
    def load_data(self, units):
        """Load units data"""
        self.units = units
        self.unit_list.clear()
        for unit in units:
            self.unit_list.addItem(f"{unit['name']} ({unit.get('faction', 'Player')})")
    
    def refresh_class_list(self):
        """Refresh the class dropdown from the classes widget"""
        current_class = self.unit_class.currentText()
        self.unit_class.clear()
        
        # Get classes from the classes widget
        classes = self.classes_widget.get_data()
        if classes:
            class_names = [cls['name'] for cls in classes]
            self.unit_class.addItems(class_names)
            self.unit_class.setEnabled(True)
            
            # Try to restore previous selection
            if current_class in class_names:
                self.unit_class.setCurrentText(current_class)
        else:
            self.unit_class.setEnabled(False)
            self.unit_class.addItem("(No classes defined)")
    
    def refresh_inventory_items(self):
        """Refresh inventory dropdowns from weapons and items widgets"""
        # Get current selections
        current_selections = [combo.currentText() for combo in self.inventory_items]
        
        # Get all weapons and items
        weapons = self.weapons_widget.get_data()
        items = self.items_widget.get_data()
        
        # Combine into one list of names
        available_items = ["(Empty)"]
        available_items.extend([weapon['name'] for weapon in weapons])
        available_items.extend([item['name'] for item in items])
        
        # Update all inventory combo boxes
        for i, combo in enumerate(self.inventory_items):
            combo.clear()
            combo.addItems(available_items)
            
            # Try to restore previous selection
            if current_selections[i] in available_items:
                combo.setCurrentText(current_selections[i])
            else:
                combo.setCurrentText("(Empty)")


    def refresh_character_list(self):
        """Refresh the character dropdown from the story editor"""
        current_char_id = self.unit_character.currentData()
        self.unit_character.clear()
        
        # Add "(None)" option
        self.unit_character.addItem("(None - Generic Unit)", None)
        
        # Get characters from story editor if available
        if self.story_editor:
            characters = self.story_editor.characters_widget.get_data()
            if characters:
                for char in characters:
                    char_id = char.get('id', '')
                    char_name = char.get('name', 'Unknown')
                    if char_id:
                        self.unit_character.addItem(f"{char_name} (ID: {char_id})", char_id)
                
                # Try to restore previous selection
                if current_char_id:
                    index = self.unit_character.findData(current_char_id)
                    if index >= 0:
                        self.unit_character.setCurrentIndex(index)


class WeaponsWidget(QWidget):
    """Widget for managing weapons"""
    
    def __init__(self):
        super().__init__()
        self.weapons = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the weapons UI"""
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Left side - weapon list
        left_layout = QVBoxLayout()
        
        left_layout.addWidget(QLabel("Weapons:"))
        self.weapon_list = QListWidget()
        self.weapon_list.currentRowChanged.connect(self.on_weapon_selected)
        self.weapon_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.weapon_list.model().rowsMoved.connect(self.on_weapon_reordered)
        left_layout.addWidget(self.weapon_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Weapon")
        add_btn.clicked.connect(self.add_weapon)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_weapon)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        left_layout.addLayout(btn_layout)
        
        layout.addLayout(left_layout, 1)
        
        # Right side - weapon details (with scroll area)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        
        details_group = QGroupBox("Weapon Details")
        details_layout = QFormLayout()
        
        self.weapon_name = QLineEdit()
        self.weapon_type = QComboBox()
        self.weapon_type.addItems(["Sword", "Lance", "Axe", "Bow", "Tome", "Staff", "Special"])
        self.weapon_rank = QComboBox()
        self.weapon_rank.addItems(["E", "D", "C", "B", "A", "S", "Prf"])
        self.weapon_mt = QSpinBox()
        self.weapon_mt.setMaximum(99)
        self.weapon_hit = QSpinBox()
        self.weapon_hit.setMaximum(100)
        self.weapon_crit = QSpinBox()
        self.weapon_crit.setMaximum(100)
        self.weapon_range = QLineEdit()
        self.weapon_range.setPlaceholderText("1, 2 or 1-2")
        self.weapon_uses = QSpinBox()
        self.weapon_uses.setMaximum(99)
        self.weapon_description = QTextEdit()
        self.weapon_description.setMaximumHeight(80)
        
        details_layout.addRow("Name:", self.weapon_name)
        details_layout.addRow("Type:", self.weapon_type)
        details_layout.addRow("Rank:", self.weapon_rank)
        details_layout.addRow("Might:", self.weapon_mt)
        details_layout.addRow("Hit:", self.weapon_hit)
        details_layout.addRow("Crit:", self.weapon_crit)
        details_layout.addRow("Range:", self.weapon_range)
        details_layout.addRow("Uses:", self.weapon_uses)
        details_layout.addRow("Description:", self.weapon_description)
        
        details_group.setLayout(details_layout)
        right_layout.addWidget(details_group)
        
        right_layout.addStretch()
        
        scroll.setWidget(right_widget)
        layout.addWidget(scroll, 2)
        
    def add_weapon(self):
        """Add a new weapon"""
        weapon = {
            'name': 'New Weapon',
            'type': 'Sword',
            'rank': 'E',
            'might': 5,
            'hit': 90,
            'crit': 0,
            'range': '1',
            'uses': 45,
            'description': ''
        }
        self.weapons.append(weapon)
        self.weapon_list.addItem(weapon['name'])
        
    def remove_weapon(self):
        """Remove selected weapon"""
        row = self.weapon_list.currentRow()
        if row >= 0:
            self.weapons.pop(row)
            self.weapon_list.takeItem(row)
            
    def move_weapon_up(self):
        """Move selected weapon up in the list"""
        row = self.weapon_list.currentRow()
        if row > 0:
            # Save current weapon data
            self.update_weapon_data(row)
            # Swap in data list
            self.weapons[row], self.weapons[row - 1] = self.weapons[row - 1], self.weapons[row]
            # Update list widget with correct display text
            self.weapon_list.item(row).setText(f"{self.weapons[row]['name']} - {self.weapons[row]['type']}")
            self.weapon_list.item(row - 1).setText(f"{self.weapons[row - 1]['name']} - {self.weapons[row - 1]['type']}")
            # Move selection
            self.weapon_list.setCurrentRow(row - 1)
            
    def move_weapon_down(self):
        """Move selected weapon down in the list"""
        row = self.weapon_list.currentRow()
        if row >= 0 and row < len(self.weapons) - 1:
            # Save current weapon data
            self.update_weapon_data(row)
            # Swap in data list
            self.weapons[row], self.weapons[row + 1] = self.weapons[row + 1], self.weapons[row]
            # Update list widget with correct display text
            self.weapon_list.item(row).setText(f"{self.weapons[row]['name']} - {self.weapons[row]['type']}")
            self.weapon_list.item(row + 1).setText(f"{self.weapons[row + 1]['name']} - {self.weapons[row + 1]['type']}")
            # Move selection
            self.weapon_list.setCurrentRow(row + 1)
            
    def on_weapon_reordered(self):
        """Handle drag-and-drop reordering"""
        # Rebuild weapons list based on current list widget order
        new_order = []
        for i in range(self.weapon_list.count()):
            weapon_display = self.weapon_list.item(i).text()
            # Parse weapon name (format: "Name - Type")
            weapon_name = weapon_display.split(' - ')[0] if ' - ' in weapon_display else weapon_display
            # Find the weapon with this name
            for weapon in self.weapons:
                if weapon['name'] == weapon_name:
                    new_order.append(weapon)
                    break
        self.weapons = new_order
            
    def on_weapon_selected(self, index):
        """Handle weapon selection"""
        # Save the previously selected weapon first
        if hasattr(self, '_previous_weapon_index') and 0 <= self._previous_weapon_index < len(self.weapons):
            self.update_weapon_data(self._previous_weapon_index)
        
        if 0 <= index < len(self.weapons):
            self._previous_weapon_index = index
            
            # Disconnect any existing signals to prevent duplicate connections
            try:
                self.weapon_name.textChanged.disconnect()
                self.weapon_type.currentTextChanged.disconnect()
                self.weapon_rank.currentTextChanged.disconnect()
                self.weapon_mt.valueChanged.disconnect()
                self.weapon_hit.valueChanged.disconnect()
                self.weapon_crit.valueChanged.disconnect()
                self.weapon_range.textChanged.disconnect()
                self.weapon_uses.valueChanged.disconnect()
                self.weapon_description.textChanged.disconnect()
            except:
                pass
            
            wpn = self.weapons[index]
            self.weapon_name.setText(wpn['name'])
            self.weapon_type.setCurrentText(wpn['type'])
            self.weapon_rank.setCurrentText(wpn['rank'])
            self.weapon_mt.setValue(wpn['might'])
            self.weapon_hit.setValue(wpn['hit'])
            self.weapon_crit.setValue(wpn['crit'])
            self.weapon_range.setText(wpn['range'])
            self.weapon_uses.setValue(wpn['uses'])
            self.weapon_description.setPlainText(wpn['description'])
            
            # Connect signals to update data
            self.weapon_name.textChanged.connect(lambda text: self.update_weapon_data(index))
            self.weapon_type.currentTextChanged.connect(lambda text: self.update_weapon_data(index))
            self.weapon_rank.currentTextChanged.connect(lambda text: self.update_weapon_data(index))
            self.weapon_mt.valueChanged.connect(lambda val: self.update_weapon_data(index))
            self.weapon_hit.valueChanged.connect(lambda val: self.update_weapon_data(index))
            self.weapon_crit.valueChanged.connect(lambda val: self.update_weapon_data(index))
            self.weapon_range.textChanged.connect(lambda text: self.update_weapon_data(index))
            self.weapon_uses.valueChanged.connect(lambda val: self.update_weapon_data(index))
            self.weapon_description.textChanged.connect(lambda: self.update_weapon_data(index))
            
    def update_weapon_data(self, index):
        """Update all weapon data from UI fields"""
        if 0 <= index < len(self.weapons):
            wpn = self.weapons[index]
            wpn['name'] = self.weapon_name.text()
            wpn['type'] = self.weapon_type.currentText()
            wpn['rank'] = self.weapon_rank.currentText()
            wpn['might'] = self.weapon_mt.value()
            wpn['hit'] = self.weapon_hit.value()
            wpn['crit'] = self.weapon_crit.value()
            wpn['range'] = self.weapon_range.text()
            wpn['uses'] = self.weapon_uses.value()
            wpn['description'] = self.weapon_description.toPlainText()
            # Update the list item text
            self.weapon_list.item(index).setText(wpn['name'])
            
    def get_data(self):
        """Get weapons data"""
        # Save the currently selected weapon before returning data
        current_index = self.weapon_list.currentRow()
        if 0 <= current_index < len(self.weapons):
            self.update_weapon_data(current_index)
        return self.weapons
        
    def load_data(self, weapons):
        """Load weapons data"""
        self.weapons = weapons
        self.weapon_list.clear()
        for wpn in weapons:
            self.weapon_list.addItem(wpn['name'])


class ItemsWidget(QWidget):
    """Widget for managing items"""
    
    def __init__(self):
        super().__init__()
        self.items = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the items UI"""
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Left side - item list
        left_layout = QVBoxLayout()
        
        left_layout.addWidget(QLabel("Items:"))
        self.item_list = QListWidget()
        self.item_list.currentRowChanged.connect(self.on_item_selected)
        self.item_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.item_list.model().rowsMoved.connect(self.on_item_reordered)
        left_layout.addWidget(self.item_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Item")
        add_btn.clicked.connect(self.add_item)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_item)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        left_layout.addLayout(btn_layout)
        
        layout.addLayout(left_layout, 1)
        
        # Right side - item details (with scroll area)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        
        # Item details
        details_group = QGroupBox("Item Details")
        details_layout = QFormLayout()
        
        self.item_name = QLineEdit()
        self.item_type = QComboBox()
        self.item_type.addItems(["Consumable", "Stat Booster", "Promotion Item", "Key Item", "Special"])
        self.item_uses = QSpinBox()
        self.item_uses.setMaximum(99)
        self.item_uses.setValue(1)
        self.item_description = QTextEdit()
        self.item_description.setMaximumHeight(80)
        
        details_layout.addRow("Name:", self.item_name)
        details_layout.addRow("Type:", self.item_type)
        details_layout.addRow("Uses:", self.item_uses)
        details_layout.addRow("Description:", self.item_description)
        
        details_group.setLayout(details_layout)
        right_layout.addWidget(details_group)
        
        # Healing Properties (for Consumables)
        self.healing_group = QGroupBox("Healing Properties")
        healing_layout = QFormLayout()
        
        self.heal_hp = QSpinBox()
        self.heal_hp.setRange(0, 99)
        self.heal_hp.setValue(0)
        
        healing_layout.addRow("HP Restored:", self.heal_hp)
        healing_layout.addWidget(QLabel("(Amount of HP restored when used)"))
        
        self.healing_group.setLayout(healing_layout)
        right_layout.addWidget(self.healing_group)
        
        # Stat Boost Properties (for Stat Boosters)
        self.stat_boost_group = QGroupBox("Stat Boost Properties")
        stat_boost_layout = QFormLayout()
        
        stat_boost_layout.addWidget(QLabel("Permanent stat increases:"))
        
        self.boost_hp = QSpinBox()
        self.boost_str = QSpinBox()
        self.boost_mag = QSpinBox()
        self.boost_skl = QSpinBox()
        self.boost_spd = QSpinBox()
        self.boost_lck = QSpinBox()
        self.boost_def = QSpinBox()
        self.boost_res = QSpinBox()
        
        for spin in [self.boost_hp, self.boost_str, self.boost_mag, self.boost_skl,
                     self.boost_spd, self.boost_lck, self.boost_def, self.boost_res]:
            spin.setRange(0, 30)
            spin.setValue(0)
            
        stat_boost_layout.addRow("HP Boost:", self.boost_hp)
        stat_boost_layout.addRow("STR Boost:", self.boost_str)
        stat_boost_layout.addRow("MAG Boost:", self.boost_mag)
        stat_boost_layout.addRow("SKL Boost:", self.boost_skl)
        stat_boost_layout.addRow("SPD Boost:", self.boost_spd)
        stat_boost_layout.addRow("LCK Boost:", self.boost_lck)
        stat_boost_layout.addRow("DEF Boost:", self.boost_def)
        stat_boost_layout.addRow("RES Boost:", self.boost_res)
        
        self.stat_boost_group.setLayout(stat_boost_layout)
        right_layout.addWidget(self.stat_boost_group)
        
        # Promotion Properties (for Promotion Items)
        self.promotion_group = QGroupBox("Promotion Properties")
        promotion_layout = QFormLayout()
        
        self.promotion_target = QLineEdit()
        self.promotion_target.setPlaceholderText("e.g., Knight, Paladin, General")
        
        promotion_layout.addRow("Target Class:", self.promotion_target)
        promotion_layout.addWidget(QLabel("(Class this item promotes to, leave blank for any)"))
        
        self.promotion_group.setLayout(promotion_layout)
        right_layout.addWidget(self.promotion_group)
        
        # Key Item Properties
        self.key_item_group = QGroupBox("Key Item Properties")
        key_item_layout = QFormLayout()
        
        self.key_item_id = QLineEdit()
        self.key_item_id.setPlaceholderText("e.g., village_key, door_key_1")
        
        key_item_layout.addRow("Key Item ID:", self.key_item_id)
        key_item_layout.addWidget(QLabel("(Unique identifier for scripts/events)"))
        
        self.key_item_group.setLayout(key_item_layout)
        right_layout.addWidget(self.key_item_group)
        
        # Special Item Properties
        self.special_group = QGroupBox("Special Item Properties")
        special_layout = QFormLayout()
        
        self.special_effect = QTextEdit()
        self.special_effect.setMaximumHeight(60)
        self.special_effect.setPlaceholderText("Describe custom effect...")
        
        special_layout.addRow("Custom Effect:", self.special_effect)
        
        self.special_group.setLayout(special_layout)
        right_layout.addWidget(self.special_group)
        
        # Connect item type change to show/hide relevant sections
        self.item_type.currentTextChanged.connect(self.update_property_visibility)
        
        right_layout.addStretch()
        
        scroll.setWidget(right_widget)
        layout.addWidget(scroll, 2)
        
        # Initialize property visibility
        self.update_property_visibility()
        
    def update_property_visibility(self):
        """Show/hide property groups based on item type"""
        item_type = self.item_type.currentText()
        
        # Hide all groups first
        self.healing_group.hide()
        self.stat_boost_group.hide()
        self.promotion_group.hide()
        self.key_item_group.hide()
        self.special_group.hide()
        
        # Show relevant groups
        if item_type == "Consumable":
            self.healing_group.show()
        elif item_type == "Stat Booster":
            self.stat_boost_group.show()
        elif item_type == "Promotion Item":
            self.promotion_group.show()
        elif item_type == "Key Item":
            self.key_item_group.show()
        elif item_type == "Special":
            self.special_group.show()
        
    def add_item(self):
        """Add a new item"""
        item = {
            'name': 'New Item',
            'type': 'Consumable',
            'uses': 1,
            'description': '',
            'properties': {
                'heal_hp': 0,
                'boost_hp': 0,
                'boost_str': 0,
                'boost_mag': 0,
                'boost_skl': 0,
                'boost_spd': 0,
                'boost_lck': 0,
                'boost_def': 0,
                'boost_res': 0,
                'promotion_target': '',
                'key_item_id': '',
                'special_effect': ''
            }
        }
        self.items.append(item)
        self.item_list.addItem(item['name'])
        self.item_list.setCurrentRow(len(self.items) - 1)
        
    def remove_item(self):
        """Remove selected item"""
        row = self.item_list.currentRow()
        if row >= 0:
            self.items.pop(row)
            self.item_list.takeItem(row)
            
    def move_item_up(self):
        """Move selected item up in the list"""
        row = self.item_list.currentRow()
        if row > 0:
            # Save current item data
            self.update_item_data(row)
            # Swap in data list
            self.items[row], self.items[row - 1] = self.items[row - 1], self.items[row]
            # Update list widget with correct names
            self.item_list.item(row).setText(self.items[row]['name'])
            self.item_list.item(row - 1).setText(self.items[row - 1]['name'])
            # Move selection
            self.item_list.setCurrentRow(row - 1)
            
    def move_item_down(self):
        """Move selected item down in the list"""
        row = self.item_list.currentRow()
        if row >= 0 and row < len(self.items) - 1:
            # Save current item data
            self.update_item_data(row)
            # Swap in data list
            self.items[row], self.items[row + 1] = self.items[row + 1], self.items[row]
            # Update list widget with correct names
            self.item_list.item(row).setText(self.items[row]['name'])
            self.item_list.item(row + 1).setText(self.items[row + 1]['name'])
            # Move selection
            self.item_list.setCurrentRow(row + 1)
            
    def on_item_reordered(self):
        """Handle drag-and-drop reordering"""
        # Rebuild items list based on current list widget order
        new_order = []
        for i in range(self.item_list.count()):
            item_name = self.item_list.item(i).text()
            # Find the item with this name
            for item in self.items:
                if item['name'] == item_name:
                    new_order.append(item)
                    break
        self.items = new_order
            
    def on_item_selected(self, index):
        """Handle item selection"""
        # Save the previously selected item first
        if hasattr(self, '_previous_item_index') and 0 <= self._previous_item_index < len(self.items):
            self.update_item_data(self._previous_item_index)
        
        if 0 <= index < len(self.items):
            self._previous_item_index = index
            
            # Disconnect any existing signals to prevent duplicate connections
            try:
                self.item_name.textChanged.disconnect()
                self.item_type.currentTextChanged.disconnect()
                self.item_uses.valueChanged.disconnect()
                self.item_description.textChanged.disconnect()
                self.heal_hp.valueChanged.disconnect()
                self.boost_hp.valueChanged.disconnect()
                self.boost_str.valueChanged.disconnect()
                self.boost_mag.valueChanged.disconnect()
                self.boost_skl.valueChanged.disconnect()
                self.boost_spd.valueChanged.disconnect()
                self.boost_lck.valueChanged.disconnect()
                self.boost_def.valueChanged.disconnect()
                self.boost_res.valueChanged.disconnect()
                self.promotion_target.textChanged.disconnect()
                self.key_item_id.textChanged.disconnect()
                self.special_effect.textChanged.disconnect()
            except:
                pass
            
            item = self.items[index]
            self.item_name.setText(item['name'])
            self.item_type.setCurrentText(item['type'])
            self.item_uses.setValue(item['uses'])
            self.item_description.setPlainText(item['description'])
            
            # Load properties (backward compatible with old 'effects' structure)
            props = item.get('properties', item.get('effects', {}))
            self.heal_hp.setValue(props.get('heal_hp', props.get('hp', 0)))
            self.boost_hp.setValue(props.get('boost_hp', 0))
            self.boost_str.setValue(props.get('boost_str', props.get('str', 0)))
            self.boost_mag.setValue(props.get('boost_mag', props.get('mag', 0)))
            self.boost_skl.setValue(props.get('boost_skl', props.get('skl', 0)))
            self.boost_spd.setValue(props.get('boost_spd', props.get('spd', 0)))
            self.boost_lck.setValue(props.get('boost_lck', props.get('lck', 0)))
            self.boost_def.setValue(props.get('boost_def', props.get('def', 0)))
            self.boost_res.setValue(props.get('boost_res', props.get('res', 0)))
            self.promotion_target.setText(props.get('promotion_target', ''))
            self.key_item_id.setText(props.get('key_item_id', ''))
            self.special_effect.setPlainText(props.get('special_effect', ''))
            
            # Update visibility based on type
            self.update_property_visibility()
            
            # Connect signals to update data
            self.item_name.textChanged.connect(lambda text: self.update_item_data(index))
            self.item_type.currentTextChanged.connect(lambda text: self.update_item_data(index))
            self.item_uses.valueChanged.connect(lambda val: self.update_item_data(index))
            self.item_description.textChanged.connect(lambda: self.update_item_data(index))
            self.heal_hp.valueChanged.connect(lambda val: self.update_item_data(index))
            self.boost_hp.valueChanged.connect(lambda val: self.update_item_data(index))
            self.boost_str.valueChanged.connect(lambda val: self.update_item_data(index))
            self.boost_mag.valueChanged.connect(lambda val: self.update_item_data(index))
            self.boost_skl.valueChanged.connect(lambda val: self.update_item_data(index))
            self.boost_spd.valueChanged.connect(lambda val: self.update_item_data(index))
            self.boost_lck.valueChanged.connect(lambda val: self.update_item_data(index))
            self.boost_def.valueChanged.connect(lambda val: self.update_item_data(index))
            self.boost_res.valueChanged.connect(lambda val: self.update_item_data(index))
            self.promotion_target.textChanged.connect(lambda text: self.update_item_data(index))
            self.key_item_id.textChanged.connect(lambda text: self.update_item_data(index))
            self.special_effect.textChanged.connect(lambda: self.update_item_data(index))
            
    def update_item_data(self, index):
        """Update all item data from UI fields"""
        if 0 <= index < len(self.items):
            item = self.items[index]
            item['name'] = self.item_name.text()
            item['type'] = self.item_type.currentText()
            item['uses'] = self.item_uses.value()
            item['description'] = self.item_description.toPlainText()
            item['properties'] = {
                'heal_hp': self.heal_hp.value(),
                'boost_hp': self.boost_hp.value(),
                'boost_str': self.boost_str.value(),
                'boost_mag': self.boost_mag.value(),
                'boost_skl': self.boost_skl.value(),
                'boost_spd': self.boost_spd.value(),
                'boost_lck': self.boost_lck.value(),
                'boost_def': self.boost_def.value(),
                'boost_res': self.boost_res.value(),
                'promotion_target': self.promotion_target.text(),
                'key_item_id': self.key_item_id.text(),
                'special_effect': self.special_effect.toPlainText()
            }
            # Update the list item text
            self.item_list.item(index).setText(item['name'])
    
    def get_data(self):
        """Get items data"""
        # Save the currently selected item before returning data
        current_index = self.item_list.currentRow()
        if 0 <= current_index < len(self.items):
            self.update_item_data(current_index)
        return self.items
        
    def load_data(self, items):
        """Load items data"""
        self.items = items
        self.item_list.clear()
        for item in items:
            self.item_list.addItem(item['name'])


class StatsWidget(QWidget):
    """Widget for configuring stat system"""
    
    def __init__(self):
        super().__init__()
        self.stats_config = {}
        self.init_ui()
        
    def init_ui(self):
        """Initialize the stats UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        layout.addWidget(QLabel("Stats Configuration"))
        layout.addWidget(QLabel("Configure the stat system for your game"))
        
        # Stats table
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(3)
        self.stats_table.setHorizontalHeaderLabels(["Stat Name", "Min Value", "Max Value"])
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Add default stats
        default_stats = [
            ("HP", 1, 99),
            ("STR", 0, 30),
            ("MAG", 0, 30),
            ("SKL", 0, 30),
            ("SPD", 0, 30),
            ("LCK", 0, 30),
            ("DEF", 0, 30),
            ("RES", 0, 30)
        ]
        
        self.stats_table.setRowCount(len(default_stats))
        for i, (name, min_val, max_val) in enumerate(default_stats):
            self.stats_table.setItem(i, 0, QTableWidgetItem(name))
            self.stats_table.setItem(i, 1, QTableWidgetItem(str(min_val)))
            self.stats_table.setItem(i, 2, QTableWidgetItem(str(max_val)))
            
        layout.addWidget(self.stats_table)
        
    def get_data(self):
        """Get stats configuration"""
        config = {}
        for i in range(self.stats_table.rowCount()):
            name = self.stats_table.item(i, 0).text().lower()
            min_val = int(self.stats_table.item(i, 1).text())
            max_val = int(self.stats_table.item(i, 2).text())
            config[name] = {'min': min_val, 'max': max_val}
        return config
        
    def load_data(self, stats):
        """Load stats configuration"""
        self.stats_config = stats
