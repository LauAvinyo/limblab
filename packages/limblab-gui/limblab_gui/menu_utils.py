from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMenu,
    QToolButton,
    QWidget,
    QVBoxLayout,
    QScrollArea
)
from PyQt6.QtGui import (
    QAction)
import webbrowser
from limblab.design import theme
from utils import (
    create_back_button,
    create_collapsible_section
    
)
from mixin.NavigationMixin import NavigationMixin

class MenuUtils:    
    def _build_home_topbar(self):
        """Home-page branding bar."""
        bar = QWidget()
        bar.setStyleSheet(f"""
                background-color: {theme('palette.primary', '#0D7C66')};
            """)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(30, 0, 30, 0)

        title = QLabel("LimbLab")
        title.setStyleSheet(f"color: {theme('palette.textPrimary', '#FFFFFF')}; font-weight: bold; padding: 20px 0px;")
        layout.addWidget(title)
        layout.addStretch()

        resources_btn = QToolButton()
        resources_btn.setText("Resources")
        resources_menu = QMenu(resources_btn)
        paper = QAction("Paper", self)
        paper.triggered.connect(lambda: webbrowser.open("https://pmc.ncbi.nlm.nih.gov/articles/PMC12794269/"))
        resources_menu.addAction(paper)
        github = QAction("GitHub", self)
        github.triggered.connect(lambda: webbrowser.open("https://limblab.embl.es/docs/"))
        resources_menu.addAction(github)
        resources_btn.setMenu(resources_menu)
        resources_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        layout.addWidget(resources_btn)

        aboutus_btn = QToolButton()
        aboutus_btn.setText("About us")
        aboutus_btn.clicked.connect(lambda: webbrowser.open("https://www.embl.org/groups/sharpe/"))
        layout.addWidget(aboutus_btn)

        contact= QToolButton()
        contact.setText("Contact us")
        contact_menu = QMenu(contact)
        
        contact_menu.addAction(QAction("EMBL, Barcelona", self))
        contact_menu.addAction(QAction("info@embl.es", self))

        contact.setMenu(contact_menu)
        contact.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        layout.addWidget(contact)

        return bar

    def _refresh_pipeline_actions(self, current_step=None):
        self.action_bar.setVisible(True)
        self._current_pipeline_step = current_step 

        for idx, step in enumerate(self.PIPELINE_STEPS):
            act = self._step_actions[step]
            flag = self.STEP_DONE_FLAG.get(step)
            is_done = bool(flag and self.workflow_state.get(flag))
            is_reachable = all(
                    self.workflow_state.get(self.STEP_DONE_FLAG[s])
                    for s in self.PIPELINE_STEPS[:idx] if s in self.STEP_DONE_FLAG
                )
            act.setText(("✓ " if is_done else '🔒︎ ' if not is_reachable else "") + step)
            act.setEnabled(is_reachable)
            act.setChecked(step == current_step)


    def _build_resources_menu(self, menu):
        """Build the Resources submenu."""
        resources = menu.addMenu("Resources")
        paper = QAction("Paper", self)
        paper.triggered.connect(
                lambda: webbrowser.open(
                    "https://pmc.ncbi.nlm.nih.gov/articles/PMC12794269/"
                )
            )
        resources.addAction(paper)

        github = QAction("GitHub", self)
        github.triggered.connect(
                lambda: webbrowser.open("https://limblab.embl.es/docs/")
            )
        resources.addAction(github)
        return resources

    def _build_contact_menu(self, menu):
        """Build the Contact us submenu."""
        contact = menu.addMenu("Contact us")

        contact.addAction(QAction("EMBL, Barcelona", self))
        contact.addAction(QAction("info@embl.es", self))
        return contact

    def _build_view_menu(self, menu_bar):
        """Build the View menu."""
        view_menu = menu_bar.addMenu("&View")
        view_menu.addAction(QAction("Visualization Mode", self))

        viz_modes = ["Isosurface", "Slices", "Raycast", "Probe", "2D Projection Slab"]
        for mode in viz_modes:
            action = QAction(mode, self)  # , checkable=True
            action.triggered.connect(lambda checked, m=mode: self.add_viz_section(m))
            view_menu.addAction(action)#modification to select viz mode!!!
        return view_menu


    def _build_permanent_chrome(self):
        if getattr(self, "_chrome_built", False):
            return
        self._chrome_built = True

        menu_bar = self.menuBar()
        menu_bar.setStyleSheet(f"""
                QMenuBar {{ background-color: {theme('#123467', '#141414')};
                            color: {theme('palette.textSecondary', '#A0A0A0')}; border: none; }}
                QMenuBar::item:selected {{ background-color: {theme('palette.panel', '#2A2A2A')};
                            color: {theme('palette.textPrimary', '#FFFFFF')}; border-radius: 4px; }}
            """)

        self.action_bar = self.addToolBar("Pipeline")
        self.action_bar.setMovable(False)
        self.action_bar.setStyleSheet(f"""
                QToolBar {{ background-color: {theme('palette.background', '#141414')}; border: none; spacing: 4px; padding: 4px; }}
                QToolButton {{ color: {theme('palette.textSecondary', '#A0A0A0')}; padding: 6px 14px; border-radius: 4px; }}
                QToolButton:disabled {{ color: {theme('palette.textDisabled', '#3A3A3A')}; }}
                QToolButton:checked {{ background-color: {theme('palette.panel', '#2A2A2A')}; color: {theme('palette.textPrimary', '#FFFFFF')}; }}
            """)

            # Same back button widget show_exp/show_first_screen use — real QWidget,
            # so addWidget (not addAction).
        self._active_back_guard = None
        self.back_btn = create_back_button(
            lambda: self._handle_back(self._current_pipeline_step, self._active_back_guard))
        self.action_bar.addWidget(self.back_btn)
        self.action_bar.addSeparator()

        self._current_pipeline_step = None
        self._step_actions = {}
        for step in self.PIPELINE_STEPS:
            act = QAction(step, self)
            act.setCheckable(True)
            act.triggered.connect(lambda checked=False, s=step: self.navigate_to_step(s, self._current_pipeline_step))
            self.action_bar.addAction(act)
            self._step_actions[step] = act

        self.action_bar.setVisible(False)


    def _reset_workflow_from(self, step):
        """Clear *_done flags for `step` and everything after it, so the
            toolbar re-locks those steps until they're redone. Called only after
            the user has explicitly confirmed they want to overwrite prior output."""
        idx = self.PIPELINE_STEPS.index(step)
        for s in self.PIPELINE_STEPS[idx:]:
            flag = self.STEP_DONE_FLAG.get(s)
            if flag:
                self.workflow_state[flag] = False

            # fields that ride alongside the *_done flags
        if idx <= self.PIPELINE_STEPS.index("Clean"):
            self.workflow_state["last_cleaned_channel"] = None
        if idx <= self.PIPELINE_STEPS.index("Stage"):
            self.workflow_state["selected_stage"] = None
        if idx <= self.PIPELINE_STEPS.index("Align"):
            self.workflow_state["alignment_method"] = None
            self.align.source = None
            self.align.surface_path = None

        self._refresh_pipeline_actions(current_step=step)
        self.log_pipeline(f"Reset workflow state from '{step}' onward — redoing this step.")


    def _build_side_panel(self):
        """Build the collapsible right-side panel."""
        panel = QWidget()
        panel.setFixedWidth(260)
        panel.setStyleSheet(f"background-color: {theme('palette.surface', '#1E1E1E')};")

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{ border: none; background-color: {theme('palette.surface', '#1E1E1E')}; }}
            QScrollBar:vertical {{ border: none; background: {theme('palette.panel', '#2A2A2A')}; width: 10px; margin: 0px; }}
            QScrollBar::handle:vertical {{ background: {theme('palette.primaryHover', '#41B3A2')}; border-radius: 5px; min-height: 20px; }}
            QScrollBar::handle:vertical:hover {{ background: {theme('palette.primary', '#5FBF9F')}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ border: none; background: none; }}
        """)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(2)

        # Visualizer section
        self.visualizer_content = QWidget()
        outer_viz_layout = QVBoxLayout(self.visualizer_content)
        outer_viz_layout.setContentsMargins(10, 6, 10, 10)
        outer_viz_layout.setSpacing(6)

        self.visualizer_list = QVBoxLayout()
        outer_viz_layout.addLayout(self.visualizer_list)

        viz_dynamic_container = QWidget()
        self.viz_sections_layout = QVBoxLayout(viz_dynamic_container)
        self.viz_sections_layout.setContentsMargins(0, 0, 0, 0)
        self.viz_sections_layout.setSpacing(2)
        outer_viz_layout.addWidget(viz_dynamic_container)

        scroll_layout.addWidget(
            create_collapsible_section(
                "Visualizer", self.visualizer_content, expanded=True
            )
        )

        self._current_viz_section_widgets = {}
        for viz_name in self.active_viz_sections:
            vsection = self._build_viz_section(viz_name)
            self.viz_sections_layout.addWidget(vsection)
            self._current_viz_section_widgets[viz_name] = vsection

        # Pipeline section
        pipeline_content = QWidget()
        pipeline_layout = QVBoxLayout(pipeline_content)
        pipeline_layout.setContentsMargins(10, 6, 10, 10)

        self.pipeline_log_widget = QLabel(
            "\n".join(self.pipeline_log[-10:])
            if self.pipeline_log
            else "pipeline.log was automatically generated. \nNo actions yet."
        )
        self.pipeline_log_widget.setWordWrap(True)
        self.pipeline_log_widget.setStyleSheet(f"color: {theme('palette.textSecondary', '#A0A0A0')}; font-size: {theme('typography.fontSizeSmall', 12)}px;")
        pipeline_layout.addWidget(self.pipeline_log_widget)

        scroll_layout.addWidget(
            create_collapsible_section("Pipeline", pipeline_content, expanded=True)
        )

        # Dynamic sections
        dynamic_container = QWidget()
        self.dynamic_sections_layout = QVBoxLayout(dynamic_container)
        self.dynamic_sections_layout.setContentsMargins(0, 0, 0, 0)
        self.dynamic_sections_layout.setSpacing(2)
        scroll_layout.addWidget(dynamic_container)


        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(scroll_area)

        self._refresh_visualizer_list()
        return panel