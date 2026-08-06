from typing import Callable

from PyQt6.QtCore import Qt
from PIL import Image
import os
import webbrowser
import pyqtgraph as pg
import numpy as np
import pyqtgraph.opengl as gl
from PyQt6.QtGui import QAction, QIcon

from PyQt6.QtWidgets import (
    QLabel, QMainWindow, QStatusBar, QVBoxLayout,
    QWidget, QHBoxLayout, QMessageBox,
    QMenu, QToolButton, QFileDialog, QCheckBox
)

from pathlib import Path

from limblab.utils import *
from limblab.constants import *
from utils import * #for same directory utils (buttons...)

#database functions
from limblab.database import *

#from limblab.NavigationMixin import NavigationMixin

from limblab.models import Experiment, Channel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LimbLab")
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #141414;
            }
        """)
        self.setStatusBar(QStatusBar(self))

        self.db_path = Path('experiments.db')

        create_test_database(self.db_path, force=True)  # Force=True is key
        #just for TESTING

        self.experiments = []
        self.experiment_names = {}
        self.experiment_checkboxes = []
        self.experiment_metadata = {}

        if not self.db_path.exists():
            # Database doesn't exist, create it with test data
            init_db(self.db_path)
            self._create_test_data()
            print("Created new database with test data")

        else:
            # Database exists, check if it has any experiments
            experiments = list_experiments(self.db_path)
            if not experiments:
                    # Database exists but empty, generate test data
                init_db(self.db_path)
                print("Generated test data in existing database")
            else:
                print(f"Found {experiments} existing experiments")

        
        self._load_experiments_from_db()

        self.show_exp()


    def _initialize_database(self):
        """Initialize database and create test data if needed."""
        if not self.db_path.exists():
            # Database doesn't exist - create it with test data
            init_db(self.db_path)
            create_test_database(self.db_path)
            print("✅ Created new database with test data")
        else:
            # Database exists - check if it has data
            try:
                experiments = list_experiments(self.db_path)
                if not experiments:
                    # Database exists but empty - add test data
                    create_test_database(self.db_path)
                    print("✅ Added test data to existing database")
                else:
                    print(f"📂 Found {len(experiments)} existing experiments")
            except Exception as e:
                print(f"⚠️ Error reading database: {e}")
                # Recreate database with test data
                create_test_database(self.db_path, force=True)
                print("✅ Recreated database with test data")

    def _load_experiments_from_db(self):
        """Load all experiments from the database."""
        try:
            # Get list of experiment IDs from database
            exp_ids = list_experiments(self.db_path)
            self.experiments = exp_ids
            
            # Load metadata for each experiment
            self.experiment_metadata = {}
            self.experiment_names = {}
            
            for exp_id in exp_ids:
                exp_data = get_experiment(self.db_path, exp_id)
                if exp_data:
                    #jsut for TESTING
                    print(f"📊 Loaded: {exp_id}")  # DEBUG
                    # Store full experiment data
                    self.experiment_metadata[exp_id] = exp_data
                    # Set display name
                    self.experiment_names[exp_id] = exp_id
                    
            print(f"📂 Loaded {len(self.experiments)} experiments from database")
            
        except Exception as e:
            print(f"⚠️ Error loading experiments: {e}")
            self.experiments = []
            self.experiment_metadata = {}





    def show_exp(self):
            #self.reset_menu_bar()
            #self.viewer.setParent(None)
        
        self.setCentralWidget(None)

        top_row = QHBoxLayout()
        #top_row.addWidget(create_back_button(self.go_back))
        top_row.addWidget(self._create_left_button())
        top_row.addStretch()

        card_layout = QVBoxLayout()
        self.experiment_checkboxes = []

        if self.experiments:
            for exp_id in self.experiments:
                display_name = self.experiment_names.get(exp_id, exp_id)
                row = QHBoxLayout()
                
                # Get experiment metadata for additional info
                exp_data = self.experiment_metadata.get(exp_id)
                if exp_data:
                    # Show side and position if available
                    side = exp_data.side if hasattr(exp_data, 'side') else ''
                    position = exp_data.position if hasattr(exp_data, 'position') else ''
                    if side and position:
                        display_name = f"{display_name} [{side}{position}]"

                label = QLabel(display_name)
                label.setStyleSheet("color: #ffffff; font-size: 18px;")
                
                threebutton = QToolButton()
                threebutton.setIcon(QIcon("threedots.png"))
                threebutton.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
                threebutton.clicked.connect(lambda checked, p=exp_id, b=threebutton: self._click_threebuttons(p, b))
                
                checkbox = QCheckBox()
                row.addWidget(label)
                row.addWidget(checkbox)
                row.addWidget(threebutton)
                row.addStretch()
                card_layout.addLayout(row)
                self.experiment_checkboxes.append((exp_id, checkbox))
        else:
            # Show "No experiments" message
            empty_label = QLabel("No experiments in database. Click '+ Add Experiment' to get started.")
            empty_label.setStyleSheet("color: #666666; font-size: 16px;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(empty_label)

        card_layout.addStretch()

        experiments_card = QWidget()
        experiments_card.setStyleSheet("background-color: #2A2A2A; border-radius: 12px;")
        experiments_card.setLayout(card_layout)
        experiments_card.setMinimumHeight(250)

        self.add_btn = create_styled_button('+ Add Experiment', "#7C6FD6", "#8E7FD6")
        self.save_btn = create_styled_button('Save Experiment', "#4B2E83", "#5C3A9E")
        self.view_btn = create_styled_button('View', "#41B3A2", "#5FBF9F")

        self.add_btn.clicked.connect(self.addexp_button_clicked)
        self.save_btn.clicked.connect(self.saveexp_button_clicked)
        self.view_btn.clicked.connect(self.viewexp_button_clicked)

        buttons_row = QVBoxLayout()
        buttons_row.setContentsMargins(0, 20, 0, 20)

        buttons_row.addStretch(1)
        buttons_row.addWidget(self.add_btn)
        buttons_row.addSpacing(10)
        buttons_row.addWidget(self.save_btn)
        buttons_row.addSpacing(10)
        buttons_row.addWidget(self.view_btn)
        buttons_row.addStretch(1)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.addLayout(top_row)
        main_layout.addWidget(experiments_card, stretch=1)
        main_layout.addSpacing(10)
        main_layout.addLayout(buttons_row)
        main_layout.addStretch(1)
        main_layout.setContentsMargins(30, 20, 30, 5)

        self.setCentralWidget(container)



# Button Actions
    def _create_left_button(self):
        """Create the left menu button with dropdown."""
        button = QToolButton()
        button.setIcon(QIcon("left_icon.png"))
        button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        menu = QMenu(self)
        #menu.setStyleSheet(MENU_STYLE)

        home = QAction("Home", self)
        home.triggered.connect(lambda: self.navigate_to(self.show_home))
        menu.addAction(home)

        menu.addSeparator()
        self._build_resources_menu(menu)

        about = QAction("About us", self)
        about.triggered.connect(lambda: webbrowser.open('https://www.embl.org/groups/sharpe/'))
        menu.addAction(about)

        self._build_contact_menu(menu)

        button.setMenu(menu)
        return button


    def _build_resources_menu(self, menu):
            """Build the Resources submenu."""
            resources = menu.addMenu("Resources")
            paper = QAction("Paper", self)
            paper.triggered.connect(lambda: webbrowser.open('https://pmc.ncbi.nlm.nih.gov/articles/PMC12794269/'))
            resources.addAction(paper)
            
            github = QAction("GitHub", self)
            github.triggered.connect(lambda: webbrowser.open('https://limblab.embl.es/docs/'))
            resources.addAction(github)
            return resources
        
    def _build_contact_menu(self, menu):
        """Build the Contact us submenu."""
        contact = menu.addMenu("Contact us")
            
            # contact.addAction(QLabel("EMBL, Barcelona", self))
            # contact.addAction(QLabel("info@embl.es", self))
        return contact




    def addexp_button_clicked(self):
        """Add experiment button handler."""
        filepath, _ = QFileDialog.getOpenFileName(
            parent=self, caption='Select an image!',
            directory=os.getcwd(), filter='Images (*.png *.jpg *.jpeg)'
        )
        if not filepath:
            return

        if not filepath.lower().endswith((".png", ".jpg", ".jpeg")):
            QMessageBox.warning(self, "Invalid file", "Please select an image file.")
            return

        # Create new experiment from file
        try:
            exp_id = os.path.basename(filepath).split('.')[0]
            
            # Check if experiment already exists
            if exp_id in self.experiments:
                QMessageBox.warning(self, "Duplicate", f"Experiment '{exp_id}' already exists.")
                return
            
            # Create a new experiment
            new_exp = Experiment(
                experiment_id=f"{exp_id}_fake",  # Add _fake to show it's from DB
                base=os.path.dirname(filepath),
                spacing_x=0.65,
                spacing_y=0.65,
                spacing_z=2.0,
                side="L",  # Default
                position="H",  # Default
                channels=[
                    Channel(
                        experiment_id=f"{exp_id}_fake",
                        channel_name="DAPI",
                        path="dapi.vti",
                        v0=238.0,
                        v1=463.0
                    ),
                    Channel(
                        experiment_id=f"{exp_id}_fake",
                        channel_name="SHH",
                        path="shh.vti",
                        v0=174.0,
                        v1=335.0
                    ),
                ]
            )
        
            save_experiment(self.db_path, new_exp)
            #saves the added experiment into our DB!!!

            self._load_experiments_from_db()
            #diaply of the newly added experiment into the db
            self.show_exp()
            print(f"✅ Added experiment: {exp_id}_TEST")
        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add experiment: {e}")

        self.show_exp()
    
    def saveexp_button_clicked(self):
        """Save experiment button handler."""
        print(True)
    
    def viewexp_button_clicked(self):
        """View experiment button handler."""
        selected = [path for path, cb in self.experiment_checkboxes if cb.isChecked()]
        if not selected:
            QMessageBox.warning(self, "No experiment selected", "Please select an experiment to visualize.")
            return
    


app = QApplication([])
window = MainWindow()
window.show()
app.exec()