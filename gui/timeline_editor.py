"""
Timeline Editor for Lehran Engine
Node-based timeline for visualizing branching story paths and event sequences
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                              QListWidget, QGroupBox, QPushButton, QLabel,
                              QLineEdit, QTextEdit, QComboBox, QSpinBox,
                              QTreeWidget, QTreeWidgetItem, QFormLayout,
                              QMessageBox, QDialog, QDialogButtonBox,
                              QGraphicsView, QGraphicsScene, QGraphicsItem,
                              QGraphicsEllipseItem, QGraphicsRectItem,
                              QGraphicsTextItem, QGraphicsLineItem, QMenu,
                              QGraphicsPathItem, QToolBar)
from PyQt6.QtCore import Qt, QDateTime, QRectF, QPointF, QLineF
from PyQt6.QtGui import (QColor, QBrush, QPen, QFont, QPainter, QPainterPath,
                         QPolygonF, QLinearGradient, QAction)


class TimelineNode(QGraphicsRectItem):
    """A visual node representing a timeline event"""
    
    def __init__(self, event_data, x, y, width=180, height=80):
        super().__init__(0, 0, width, height)
        self.event_data = event_data
        self.width = width
        self.height = height
        
        # Set position
        self.setPos(x, y)
        
        # Make it movable and selectable
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        
        # Enable caching to improve performance
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)
        
        # Style the node
        self.update_style()
        
        # Add text
        self.text_item = QGraphicsTextItem(self)
        self.update_text()
        
        # Store connections
        self.output_connections = []  # Nodes this connects to
        self.input_connections = []   # Nodes that connect to this
        
    def update_style(self):
        """Update the visual style based on event type"""
        color = self.get_event_type_color(self.event_data.get('type', 'Story Event'))
        
        # Create gradient with better contrast
        gradient = QLinearGradient(0, 0, 0, self.height)
        gradient.setColorAt(0, color.lighter(130))
        gradient.setColorAt(0.5, color.lighter(110))
        gradient.setColorAt(1, color.darker(105))
        
        self.setBrush(QBrush(gradient))
        
        # Better border with slight shadow effect using border
        if self.isSelected():
            self.setPen(QPen(QColor(70, 130, 180), 3))
        else:
            pen = QPen(color.darker(120), 2)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            self.setPen(pen)
        
        # Round corners
        self.setRect(0, 0, self.width, self.height)
        
        # Set z-value for layering
        self.setZValue(1)
        
    def update_text(self):
        """Update the text display"""
        name = self.event_data.get('name', 'Unnamed Event')
        event_type = self.event_data.get('type', 'Story Event')
        chapter = self.event_data.get('chapter', 1)
        
        chapter_text = f"Ch.{chapter}" if chapter > 0 else "Prologue"
        
        # Format text with better styling
        text = (f"<div style='background-color: rgba(255, 255, 255, 0.85); padding: 2px; border-radius: 3px;'>"
                f"<b style='color: #1a1a1a;'>{name}</b><br/>"
                f"<i style='color: #444;'>{event_type}</i><br/>"
                f"<span style='color: #555;'>{chapter_text}</span>"
                f"</div>")
        self.text_item.setHtml(text)
        self.text_item.setTextWidth(self.width - 10)
        self.text_item.setPos(5, 5)
        
        # Set font
        font = QFont("Arial", 9)
        self.text_item.setFont(font)
        
    def get_event_type_color(self, event_type):
        """Get color for event type"""
        colors = {
            'Story Event': QColor(70, 130, 180),
            'Battle/Chapter': QColor(220, 20, 60),
            'Support Conversation': QColor(255, 140, 0),
            'Cutscene': QColor(138, 43, 226),
            'Character Recruitment': QColor(34, 139, 34),
            'Character Death': QColor(139, 0, 0),
            'Base Conversation': QColor(184, 134, 11),
            'Shop/Preparation': QColor(105, 105, 105),
            'Choice/Branch': QColor(255, 215, 0),
            'Other': QColor(100, 100, 100)
        }
        return colors.get(event_type, QColor(100, 100, 100))
        
    def contextMenuEvent(self, event):
        """Show context menu"""
        menu = QMenu()
        
        add_child_action = menu.addAction("Add Child Event")
        add_choice_action = menu.addAction("Add Choice Branch")
        menu.addSeparator()
        delete_action = menu.addAction("Delete Node")
        
        action = menu.exec(event.screenPos())
        
        if action == add_child_action:
            self.scene().create_child_node(self, branch=False)
        elif action == add_choice_action:
            self.scene().create_child_node(self, branch=True)
        elif action == delete_action:
            self.scene().delete_node(self)
            
    def itemChange(self, change, value):
        """Handle item changes"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Update all connections when node moves
            if self.scene():
                self.scene().update_connections()
        return super().itemChange(change, value)
    
    def paint(self, painter, option, widget=None):
        """Custom paint to handle zoom levels"""
        # Get the current zoom level from the view
        if widget and hasattr(widget, 'transform'):
            zoom = widget.transform().m11()
        else:
            zoom = 1.0
        
        # Hide text at extreme zoom levels to prevent rendering issues
        if zoom < 0.3 or zoom > 2.5:
            self.text_item.setVisible(False)
        else:
            self.text_item.setVisible(True)
        
        # Call parent paint
        super().paint(painter, option, widget)
        
    def get_center(self):
        """Get the center point of the node"""
        return self.sceneBoundingRect().center()
        
    def get_output_point(self):
        """Get the point where connections leave this node"""
        rect = self.sceneBoundingRect()
        return QPointF(rect.center().x(), rect.bottom())
        
    def get_input_point(self):
        """Get the point where connections enter this node"""
        rect = self.sceneBoundingRect()
        return QPointF(rect.center().x(), rect.top())


class ConnectionLine(QGraphicsPathItem):
    """A connection line between two nodes"""
    
    def __init__(self, start_node, end_node, is_choice=False):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.is_choice = is_choice
        
        # Style
        if is_choice:
            pen = QPen(QColor(255, 215, 0), 3, Qt.PenStyle.DashLine)
        else:
            pen = QPen(QColor(100, 100, 100), 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.setPen(pen)
        
        # Draw behind nodes
        self.setZValue(-1)
        
        self.update_path()
        
    def update_path(self):
        """Update the connection path"""
        start_point = self.start_node.get_output_point()
        end_point = self.end_node.get_input_point()
        
        path = QPainterPath()
        path.moveTo(start_point)
        
        # Create a curved connection
        ctrl_offset = abs(end_point.y() - start_point.y()) * 0.5
        ctrl1 = QPointF(start_point.x(), start_point.y() + ctrl_offset)
        ctrl2 = QPointF(end_point.x(), end_point.y() - ctrl_offset)
        
        path.cubicTo(ctrl1, ctrl2, end_point)
        
        # Add arrow at the end
        self.add_arrow(path, end_point, ctrl2)
        
        self.setPath(path)
        
    def add_arrow(self, path, end_point, ctrl_point):
        """Add an arrow to the end of the path"""
        # Calculate arrow direction
        dx = end_point.x() - ctrl_point.x()
        dy = end_point.y() - ctrl_point.y()
        length = (dx**2 + dy**2)**0.5
        
        if length > 0:
            dx /= length
            dy /= length
            
            arrow_size = 10
            arrow_angle = 0.5
            
            # Arrow points
            p1 = QPointF(
                end_point.x() - arrow_size * (dx - dy * arrow_angle),
                end_point.y() - arrow_size * (dy + dx * arrow_angle)
            )
            p2 = QPointF(
                end_point.x() - arrow_size * (dx + dy * arrow_angle),
                end_point.y() - arrow_size * (dy - dx * arrow_angle)
            )
            
            path.moveTo(end_point)
            path.lineTo(p1)
            path.moveTo(end_point)
            path.lineTo(p2)


class TimelineScene(QGraphicsScene):
    """Custom scene for timeline nodes"""
    
    def __init__(self, parent_editor):
        super().__init__()
        self.parent_editor = parent_editor
        self.nodes = []
        self.connections = []
        self.next_node_id = 1
        
        # Set scene size
        self.setSceneRect(-2000, -2000, 4000, 4000)
        
        # Draw grid background with subtle pattern
        self.setBackgroundBrush(QBrush(QColor(240, 240, 240)))
        
    def create_node(self, event_data, x, y):
        """Create a new node"""
        node = TimelineNode(event_data, x, y)
        self.addItem(node)
        self.nodes.append(node)
        return node
        
    def create_child_node(self, parent_node, branch=False):
        """Create a child node connected to parent"""
        # Create new event data
        event_data = {
            'id': self.next_node_id,
            'name': f'Branch {self.next_node_id}' if branch else f'Event {self.next_node_id}',
            'type': 'Choice/Branch' if branch else 'Story Event',
            'chapter': parent_node.event_data.get('chapter', 1),
            'location': '',
            'description': '',
            'participants': '',
            'notes': '',
            'linked_content': []
        }
        self.next_node_id += 1
        
        # Position below parent, offset if it's a branch
        parent_rect = parent_node.sceneBoundingRect()
        offset_x = 200 if branch and len(parent_node.output_connections) > 0 else 0
        x = parent_rect.center().x() + offset_x - 90
        y = parent_rect.bottom() + 100
        
        # Create node
        child_node = self.create_node(event_data, x, y)
        
        # Create connection
        self.create_connection(parent_node, child_node, branch)
        
        self.parent_editor.refresh_data()
        return child_node
        
    def create_connection(self, start_node, end_node, is_choice=False):
        """Create a connection between two nodes"""
        connection = ConnectionLine(start_node, end_node, is_choice)
        self.addItem(connection)
        self.connections.append(connection)
        
        start_node.output_connections.append((end_node, connection))
        end_node.input_connections.append((start_node, connection))
        
    def delete_node(self, node):
        """Delete a node and its connections"""
        # Remove connections
        for end_node, connection in node.output_connections[:]:
            self.removeItem(connection)
            self.connections.remove(connection)
            end_node.input_connections = [(n, c) for n, c in end_node.input_connections if c != connection]
            
        for start_node, connection in node.input_connections[:]:
            self.removeItem(connection)
            self.connections.remove(connection)
            start_node.output_connections = [(n, c) for n, c in start_node.output_connections if c != connection]
        
        # Remove node
        self.removeItem(node)
        self.nodes.remove(node)
        
        self.parent_editor.refresh_data()
        
    def update_connections(self):
        """Update all connection paths"""
        for connection in self.connections:
            connection.update_path()
            
    def get_timeline_data(self):
        """Extract timeline data from nodes"""
        timeline_events = []
        
        for node in self.nodes:
            event_data = node.event_data.copy()
            event_data['position'] = {'x': node.pos().x(), 'y': node.pos().y()}
            
            # Store connections
            event_data['children'] = []
            for child_node, connection in node.output_connections:
                child_id = child_node.event_data.get('id', 0)
                event_data['children'].append({
                    'id': child_id,
                    'is_choice': connection.is_choice
                })
                
            timeline_events.append(event_data)
            
        return timeline_events
        
    def load_timeline_data(self, timeline_events):
        """Load timeline data and create nodes"""
        # Clear existing
        self.clear()
        self.nodes = []
        self.connections = []
        
        if not timeline_events:
            # Create initial root node
            root_event = {
                'id': 0,
                'name': 'Start',
                'type': 'Story Event',
                'chapter': 0,
                'location': '',
                'description': 'Beginning of the game',
                'participants': '',
                'notes': '',
                'linked_content': [],
                'children': []
            }
            node = self.create_node(root_event, -90, -40)
            self.next_node_id = 1
            return
            
        # Create all nodes first
        node_map = {}
        max_id = 0
        
        for event_data in timeline_events:
            pos = event_data.get('position', {'x': 0, 'y': 0})
            node = self.create_node(event_data, pos['x'], pos['y'])
            node_map[event_data.get('id', 0)] = node
            max_id = max(max_id, event_data.get('id', 0))
            
        self.next_node_id = max_id + 1
        
        # Create connections
        for event_data in timeline_events:
            node_id = event_data.get('id', 0)
            if node_id in node_map:
                parent_node = node_map[node_id]
                
                for child_info in event_data.get('children', []):
                    child_id = child_info.get('id')
                    if child_id in node_map:
                        child_node = node_map[child_id]
                        is_choice = child_info.get('is_choice', False)
                        self.create_connection(parent_node, child_node, is_choice)


class TimelineEditor(QWidget):
    """Node-based timeline editor for visualizing branching paths"""
    
    def __init__(self):
        super().__init__()
        self.current_selected_node = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the timeline editor UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Header
        header_label = QLabel("Node-Based Timeline - Visualize branching story paths")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(header_label)
        
        # Toolbar
        toolbar = QToolBar()
        
        add_node_action = QAction("Add Root Event", self)
        add_node_action.triggered.connect(self.add_root_node)
        toolbar.addAction(add_node_action)
        
        toolbar.addSeparator()
        
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)
        
        zoom_reset_action = QAction("Reset Zoom", self)
        zoom_reset_action.triggered.connect(self.reset_zoom)
        toolbar.addAction(zoom_reset_action)
        
        layout.addWidget(toolbar)
        
        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Timeline view
        self.scene = TimelineScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view.setMinimumWidth(600)
        
        # Set view background - use both methods to ensure it works
        self.view.setBackgroundBrush(QBrush(QColor(240, 240, 240)))
        self.view.setStyleSheet("QGraphicsView { background-color: rgb(240, 240, 240); border: 1px solid #ccc; }")
        
        splitter.addWidget(self.view)
        
        # Right side - Event details
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        right_widget.setMaximumWidth(400)
        
        details_group = QGroupBox("Event Details")
        details_layout = QFormLayout()
        
        self.event_name = QLineEdit()
        self.event_name.textChanged.connect(self.update_selected_node)
        
        self.event_type = QComboBox()
        self.event_type.addItems([
            "Story Event",
            "Battle/Chapter",
            "Support Conversation",
            "Cutscene",
            "Character Recruitment",
            "Character Death",
            "Base Conversation",
            "Shop/Preparation",
            "Choice/Branch",
            "Other"
        ])
        self.event_type.currentTextChanged.connect(self.update_selected_node)
        
        self.event_chapter = QSpinBox()
        self.event_chapter.setMinimum(0)
        self.event_chapter.setMaximum(999)
        self.event_chapter.setSpecialValueText("Prologue/Before Game")
        self.event_chapter.valueChanged.connect(self.update_selected_node)
        
        self.event_location = QLineEdit()
        self.event_location.textChanged.connect(self.update_selected_node)
        
        self.event_description = QTextEdit()
        self.event_description.setMaximumHeight(120)
        self.event_description.textChanged.connect(self.update_selected_node)
        
        self.event_participants = QLineEdit()
        self.event_participants.setPlaceholderText("Character names, separated by commas")
        self.event_participants.textChanged.connect(self.update_selected_node)
        
        self.event_notes = QTextEdit()
        self.event_notes.setMaximumHeight(80)
        self.event_notes.textChanged.connect(self.update_selected_node)
        
        details_layout.addRow("Event Name:", self.event_name)
        details_layout.addRow("Event Type:", self.event_type)
        details_layout.addRow("Chapter:", self.event_chapter)
        details_layout.addRow("Location:", self.event_location)
        details_layout.addRow("Description:", self.event_description)
        details_layout.addRow("Participants:", self.event_participants)
        details_layout.addRow("Notes:", self.event_notes)
        
        details_group.setLayout(details_layout)
        right_layout.addWidget(details_group)
        
        # Instructions
        info_group = QGroupBox("How to Use")
        info_layout = QVBoxLayout()
        info_text = QLabel(
            "<b>Creating Events:</b><br/>"
            "• Right-click a node → Add Child Event (sequential)<br/>"
            "• Right-click a node → Add Choice Branch (branching path)<br/><br/>"
            "<b>Navigation:</b><br/>"
            "• Drag nodes to rearrange<br/>"
            "• Scroll to pan, use toolbar to zoom<br/>"
            "• Click a node to edit its details<br/><br/>"
            "<b>Branches:</b><br/>"
            "• Solid lines = Sequential events<br/>"
            "• Dashed gold lines = Choice branches"
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)
        
        right_layout.addStretch()
        
        splitter.addWidget(right_widget)
        splitter.setSizes([700, 400])
        
        layout.addWidget(splitter)
        
        # Connect scene selection
        self.scene.selectionChanged.connect(self.on_selection_changed)
        
        self._updating = False
        
    def add_root_node(self):
        """Add a new root node"""
        event_data = {
            'id': self.scene.next_node_id,
            'name': f'Event {self.scene.next_node_id}',
            'type': 'Story Event',
            'chapter': 1,
            'location': '',
            'description': '',
            'participants': '',
            'notes': '',
            'linked_content': [],
            'children': []
        }
        self.scene.next_node_id += 1
        
        self.scene.create_node(event_data, 0, 0)
        self.refresh_data()
        
    def zoom_in(self):
        """Zoom in the view"""
        # Limit maximum zoom to prevent rendering issues
        current_scale = self.view.transform().m11()
        if current_scale < 3.0:  # Max zoom 300%
            self.view.scale(1.2, 1.2)
        
    def zoom_out(self):
        """Zoom out the view"""
        # Limit minimum zoom to prevent rendering issues
        current_scale = self.view.transform().m11()
        if current_scale > 0.2:  # Min zoom 20%
            self.view.scale(1 / 1.2, 1 / 1.2)
        
    def reset_zoom(self):
        """Reset zoom to 100%"""
        self.view.resetTransform()
        
    def on_selection_changed(self):
        """Handle node selection change"""
        selected_items = self.scene.selectedItems()
        
        if selected_items and isinstance(selected_items[0], TimelineNode):
            self.current_selected_node = selected_items[0]
            self.load_node_details(self.current_selected_node)
        else:
            self.current_selected_node = None
            self.clear_details()
            
    def load_node_details(self, node):
        """Load node details into the form"""
        self._updating = True
        
        event = node.event_data
        self.event_name.setText(event.get('name', ''))
        self.event_type.setCurrentText(event.get('type', 'Story Event'))
        self.event_chapter.setValue(event.get('chapter', 1))
        self.event_location.setText(event.get('location', ''))
        self.event_description.setPlainText(event.get('description', ''))
        self.event_participants.setText(event.get('participants', ''))
        self.event_notes.setPlainText(event.get('notes', ''))
        
        self._updating = False
        
    def clear_details(self):
        """Clear the details form"""
        self._updating = True
        
        self.event_name.clear()
        self.event_type.setCurrentIndex(0)
        self.event_chapter.setValue(1)
        self.event_location.clear()
        self.event_description.clear()
        self.event_participants.clear()
        self.event_notes.clear()
        
        self._updating = False
        
    def update_selected_node(self):
        """Update the selected node with form data"""
        if self._updating or not self.current_selected_node:
            return
            
        event = self.current_selected_node.event_data
        event['name'] = self.event_name.text()
        event['type'] = self.event_type.currentText()
        event['chapter'] = self.event_chapter.value()
        event['location'] = self.event_location.text()
        event['description'] = self.event_description.toPlainText()
        event['participants'] = self.event_participants.text()
        event['notes'] = self.event_notes.toPlainText()
        
        # Update visual
        self.current_selected_node.update_style()
        self.current_selected_node.update_text()
        
    def refresh_data(self):
        """Refresh internal data"""
        pass
        
    def get_data(self):
        """Get timeline data"""
        return self.scene.get_timeline_data()
        
    def load_data(self, timeline_events):
        """Load timeline data"""
        self.scene.load_timeline_data(timeline_events if timeline_events else [])
        # Center view on content
        self.view.centerOn(0, 0)
