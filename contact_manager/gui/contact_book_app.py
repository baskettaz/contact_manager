import html
import sqlite3
from collections.abc import Sequence
from contextlib import closing
from pathlib import Path
from typing import TypeVar
from urllib.parse import quote

from PyQt6 import uic
from PyQt6.QtCore import QBuffer, QIODevice, QSettings, QSize, Qt, QUrl
from PyQt6.QtGui import (
    QAction,
    QColor,
    QDesktopServices,
    QFont,
    QIcon,
    QImageReader,
    QKeySequence,
    QPixmap,
    QShortcut,
)
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLayout,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

DEFAULT_DB_PATH = Path(__file__).with_name("contact_book.db")
DB_PATH = DEFAULT_DB_PATH
UI_PATH = Path(__file__).with_name("contact_book.ui")
DATABASE_SETTINGS_KEY = "database/path"
WidgetType = TypeVar("WidgetType", bound=QWidget)
LayoutType = TypeVar("LayoutType", bound=QLayout)

BASE_CONTACTS = [
    {
        "full_name": "Vesselin Tsvetanov",
        "title": "Software Engineer",
        "company": "Independent / Consulting",
        "role": "Python Developer",
        "phone": "+359 88 123 4567",
        "email": "vesselin.tsvetanov@example.com",
        "category": "Owner",
        "location": "Sofia, Bulgaria",
        "linkedin": "linkedin.com/in/vesselin-tsvetanov",
        "github": "github.com/vesselin-tsvetanov",
        "website": "www.vesselin-tsvetanov.com",
        "notes": "Technology-focused professional, focused on Python, PyQt, automation, and software design.",
    },
    {
        "full_name": "Maria Petrova",
        "title": "Team Lead",
        "company": "TechNova Solutions",
        "role": "Manager",
        "phone": "+359 88 234 5678",
        "email": "maria.petrova@technova.bg",
        "category": "Professional",
        "location": "Sofia, Bulgaria",
        "linkedin": "linkedin.com/in/maria-petrova",
        "github": "",
        "website": "",
        "notes": "Technical lead and project mentor.",
    },
    {
        "full_name": "Alex Dimitrov",
        "title": "Senior Software Engineer",
        "company": "DigitalFlow Ltd.",
        "role": "Colleague",
        "phone": "+359 87 345 6789",
        "email": "alex.dimitrov@digitalflow.bg",
        "category": "Professional",
        "location": "Plovdiv, Bulgaria",
        "linkedin": "linkedin.com/in/alex-dimitrov",
        "github": "github.com/alex-dimitrov",
        "website": "",
        "notes": "Python and architecture discussions.",
    },
    {
        "full_name": "Elena Koleva",
        "title": "Recruiter",
        "company": "TalentBridge",
        "role": "Recruitment",
        "phone": "+359 89 456 7890",
        "email": "elena.koleva@talentbridge.bg",
        "category": "Professional",
        "location": "Varna, Bulgaria",
        "linkedin": "linkedin.com/in/elena-koleva",
        "github": "",
        "website": "",
        "notes": "Primary hiring contact.",
    },
    {
        "full_name": "Nikolay Petrov",
        "title": "Business Partner",
        "company": "EastBridge Consulting",
        "role": "Partner",
        "phone": "+359 88 567 8901",
        "email": "nikolay.petrov@eastbridge.bg",
        "category": "Professional",
        "location": "Burgas, Bulgaria",
        "linkedin": "linkedin.com/in/nikolay-petrov",
        "github": "",
        "website": "",
        "notes": "Project collaboration and client coordination.",
    },
    {
        "full_name": "Sofia Marinova",
        "title": "Accountant",
        "company": "Freelance Finance Group",
        "role": "Service Provider",
        "phone": "+359 87 678 9012",
        "email": "sofia.marinova@freelancefinance.bg",
        "category": "Professional",
        "location": "Sofia, Bulgaria",
        "linkedin": "linkedin.com/in/sofia-marinova",
        "github": "",
        "website": "",
        "notes": "Budget and invoicing support.",
    },
    {
        "full_name": "Ivan Karadzhov",
        "title": "Legal Advisor",
        "company": "Karadzhov & Partners",
        "role": "Advisor",
        "phone": "+359 89 789 0123",
        "email": "ivan.karadzhov@karadzovpartners.bg",
        "category": "Professional",
        "location": "Sofia, Bulgaria",
        "linkedin": "linkedin.com/in/ivan-karadzhov",
        "github": "",
        "website": "",
        "notes": "Contract and legal review.",
    },
    {
        "full_name": "George Radev",
        "title": "IT Support",
        "company": "NovaTech Services",
        "role": "Technical Support",
        "phone": "+359 88 890 1234",
        "email": "george.radev@novatech.bg",
        "category": "Professional",
        "location": "Ruse, Bulgaria",
        "linkedin": "linkedin.com/in/george-radev",
        "github": "",
        "website": "",
        "notes": "Hardware and system support.",
    },
    {
        "full_name": "Svetla Tsvetanova",
        "title": "Mother",
        "company": "Family",
        "role": "Family Contact",
        "phone": "+359 87 111 2233",
        "email": "svetla@example.com",
        "category": "Personal",
        "location": "Sofia, Bulgaria",
        "linkedin": "",
        "github": "",
        "website": "",
        "notes": "Primary family emergency contact.",
    },
    {
        "full_name": "Dimitar Tsvetanov",
        "title": "Father",
        "company": "Family",
        "role": "Family Contact",
        "phone": "+359 88 222 3344",
        "email": "dimitar@example.com",
        "category": "Personal",
        "location": "Sofia, Bulgaria",
        "linkedin": "",
        "github": "",
        "website": "",
        "notes": "Secondary family contact.",
    },
    {
        "full_name": "Yana Ivanova",
        "title": "Partner",
        "company": "Family",
        "role": "Personal Support",
        "phone": "+359 89 333 4455",
        "email": "yana.ivanova@example.com",
        "category": "Personal",
        "location": "Sofia, Bulgaria",
        "linkedin": "",
        "github": "",
        "website": "",
        "notes": "Personal support and schedule coordination.",
    },
    {
        "full_name": "Emergency Services",
        "title": "Emergency",
        "company": "Bulgaria",
        "role": "Emergency Contact",
        "phone": "112",
        "email": "",
        "category": "Emergency",
        "location": "Bulgaria",
        "linkedin": "",
        "github": "",
        "website": "",
        "notes": "For urgent situations.",
    },
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def split_full_name(full_name: str) -> tuple[str, str]:
    parts = full_name.strip().split(maxsplit=1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return (parts[0], "") if parts else ("", "")


def split_location(location: str) -> tuple[str, str]:
    parts = [part.strip() for part in location.rsplit(",", maxsplit=1)]
    if len(parts) == 2:
        return parts[0], parts[1]
    return "", parts[0] if parts else ""


def init_database(seed_if_empty: bool = True) -> None:
    with closing(get_connection()) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                first_name TEXT NOT NULL DEFAULT '',
                last_name TEXT NOT NULL DEFAULT '',
                title TEXT,
                company TEXT,
                role TEXT,
                phone TEXT,
                email TEXT,
                category TEXT,
                location TEXT,
                country TEXT NOT NULL DEFAULT '',
                linkedin TEXT,
                github TEXT,
                website TEXT,
                notes TEXT,
                photo BLOB
            )
            """
        )
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(contacts)")}
        if "first_name" not in columns:
            conn.execute(
                "ALTER TABLE contacts ADD COLUMN first_name TEXT NOT NULL DEFAULT ''"
            )
        if "last_name" not in columns:
            conn.execute(
                "ALTER TABLE contacts ADD COLUMN last_name TEXT NOT NULL DEFAULT ''"
            )
        if "country" not in columns:
            conn.execute(
                "ALTER TABLE contacts ADD COLUMN country TEXT NOT NULL DEFAULT ''"
            )
        if "photo" not in columns:
            conn.execute("ALTER TABLE contacts ADD COLUMN photo BLOB")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS contact_methods (
                contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
                kind TEXT NOT NULL CHECK(kind IN ('phone', 'email', 'website')),
                position INTEGER NOT NULL,
                value TEXT NOT NULL,
                PRIMARY KEY (contact_id, kind, position)
            )
            """
        )
        contact_methods_schema = conn.execute(
            """
            SELECT sql FROM sqlite_master
            WHERE type = 'table' AND name = 'contact_methods'
            """
        ).fetchone()
        if contact_methods_schema is not None and "'email'" not in str(
            contact_methods_schema["sql"]
        ):
            conn.execute(
                """
                CREATE TABLE contact_methods_new (
                    contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
                    kind TEXT NOT NULL CHECK(kind IN ('phone', 'email', 'website')),
                    position INTEGER NOT NULL,
                    value TEXT NOT NULL,
                    PRIMARY KEY (contact_id, kind, position)
                )
                """
            )
            conn.execute(
                """
                INSERT INTO contact_methods_new (contact_id, kind, position, value)
                SELECT contact_id, kind, position, value FROM contact_methods
                """
            )
            conn.execute("DROP TABLE contact_methods")
            conn.execute("ALTER TABLE contact_methods_new RENAME TO contact_methods")

        legacy_contacts = conn.execute(
            """
            SELECT id, full_name FROM contacts
            WHERE TRIM(first_name) = '' OR TRIM(last_name) = ''
            """
        ).fetchall()
        for contact in legacy_contacts:
            first_name, last_name = split_full_name(contact["full_name"])
            conn.execute(
                """
                UPDATE contacts
                SET first_name = CASE
                        WHEN TRIM(first_name) = '' THEN ? ELSE first_name
                    END,
                    last_name = CASE
                        WHEN TRIM(last_name) = '' THEN ? ELSE last_name
                    END
                WHERE id = ? AND (TRIM(first_name) = '' OR TRIM(last_name) = '')
                """,
                (first_name, last_name, contact["id"]),
            )

        legacy_locations = conn.execute(
            """
            SELECT id, location FROM contacts
            WHERE TRIM(country) = '' AND TRIM(COALESCE(location, '')) != ''
            """
        ).fetchall()
        for contact in legacy_locations:
            location, country = split_location(contact["location"])
            conn.execute(
                """
                UPDATE contacts
                SET location = ?, country = ?
                WHERE id = ? AND TRIM(country) = ''
                """,
                (location, country, contact["id"]),
            )

        existing_count = conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
        if existing_count == 0 and seed_if_empty:
            conn.executemany(
                """
                INSERT INTO contacts (
                    full_name, first_name, last_name, title, company, role, phone, email,
                    category, location, country, linkedin, github, website, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        item["full_name"],
                        *split_full_name(item["full_name"]),
                        item["title"],
                        item["company"],
                        item["role"],
                        item["phone"],
                        item["email"],
                        item["category"],
                        *split_location(item["location"]),
                        item["linkedin"],
                        item["github"],
                        item["website"],
                        item["notes"],
                    )
                    for item in BASE_CONTACTS
                ],
            )
        conn.commit()


class ContactBookWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.selected_contact_id: int | None = None
        self.contact_photo: bytes | None = None
        self.phone_inputs: list[QLineEdit] = []
        self.phone_remove_buttons: list[QPushButton] = []
        self.email_inputs: list[QLineEdit] = []
        self.email_remove_buttons: list[QPushButton] = []
        self.website_inputs: list[QLineEdit] = []
        self.website_remove_buttons: list[QPushButton] = []
        if not UI_PATH.is_file():
            raise FileNotFoundError(f"Runtime UI file was not found: {UI_PATH}")
        uic.loadUi(str(UI_PATH), self)
        self.resize(1440, 900)
        self.setWindowTitle("Northstar - Contact Book")
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet(self.theme_stylesheet())

        self.search_input = self.require_widget(QLineEdit, "searchInput")
        self.table = self.require_widget(QTableWidget, "contactTable")
        self.empty_state = self.require_widget(QLabel, "emptyStateLabel")
        self.first_name = self.require_widget(QLineEdit, "firstNameInput")
        self.last_name = self.require_widget(QLineEdit, "lastNameInput")
        self.title = self.require_widget(QLineEdit, "jobTitleInput")
        self.company = self.require_widget(QLineEdit, "companyInput")
        self.role = self.require_widget(QLineEdit, "roleInput")
        self.category = self.require_widget(QComboBox, "categoryInput")
        self.location = self.require_widget(QLineEdit, "locationInput")
        self.country = self.require_widget(QLineEdit, "countryInput")
        self.linkedin = self.require_widget(QLineEdit, "linkedinInput")
        self.github = self.require_widget(QLineEdit, "githubInput")
        self.notes = self.require_widget(QTextEdit, "notesInput")
        self.phone_entries_layout = self.require_layout(
            QVBoxLayout, "phoneEntriesLayout"
        )
        self.email_entries_layout = self.require_layout(
            QVBoxLayout, "emailEntriesLayout"
        )
        self.website_entries_layout = self.require_layout(
            QVBoxLayout, "websiteEntriesLayout"
        )
        self.add_phone_button = self.require_widget(QPushButton, "addPhoneButton")
        self.add_email_button = self.require_widget(QPushButton, "addEmailButton")
        self.add_website_button = self.require_widget(QPushButton, "addWebsiteButton")
        self.photo_preview = self.require_widget(QLabel, "photoPreview")
        self.choose_photo_button = self.require_widget(QPushButton, "choosePhotoButton")
        self.remove_photo_button = self.require_widget(QPushButton, "removePhotoButton")
        self.category.setEditable(True)
        self.category.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        category_line_edit = self.category.lineEdit()
        if category_line_edit is None:
            raise RuntimeError("The editable category field is unavailable.")
        category_line_edit.setPlaceholderText("Type or choose a category")

        self.add_button = self.require_widget(QPushButton, "addContactButton")
        self.save_button = self.require_widget(QPushButton, "saveContactButton")
        self.new_button = self.require_widget(QPushButton, "newContactButton")
        self.delete_button = self.require_widget(QPushButton, "deleteContactButton")
        self.list_title = self.require_widget(QLabel, "listTitle")

        self.configure_menus()
        self.add_contact_method_input("phone")
        self.add_contact_method_input("email")
        self.add_contact_method_input("website")
        self.configure_table()
        self.configure_navigation()
        self.connect_signals()
        self.refresh_table(select_first=True)

    def require_widget(self, widget_type: type[WidgetType], name: str) -> WidgetType:
        widget = self.findChild(widget_type, name)
        if widget is None:
            raise RuntimeError(
                f"Required UI widget '{name}' is missing from {UI_PATH}."
            )
        return widget

    def require_layout(self, layout_type: type[LayoutType], name: str) -> LayoutType:
        layout = self.findChild(layout_type, name)
        if layout is None:
            raise RuntimeError(
                f"Required UI layout '{name}' is missing from {UI_PATH}."
            )
        return layout

    def configure_menus(self) -> None:
        menu_bar = self.menuBar()
        if menu_bar is None:
            raise RuntimeError("The application menu bar is unavailable.")

        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)
        new_contact_action = QAction("&New contact", self)
        file_menu.addAction(new_contact_action)
        new_contact_action.setShortcut(QKeySequence.StandardKey.New)
        new_contact_action.triggered.connect(lambda: self.create_new_contact())
        save_contact_action = QAction("&Save contact", self)
        file_menu.addAction(save_contact_action)
        save_contact_action.setShortcut(QKeySequence.StandardKey.Save)
        save_contact_action.triggered.connect(lambda: self.save_contact())
        file_menu.addSeparator()
        open_database_folder_action = QAction("Open database &folder", self)
        file_menu.addAction(open_database_folder_action)
        open_database_folder_action.triggered.connect(
            lambda: self.open_database_folder()
        )
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        file_menu.addAction(exit_action)
        exit_action.triggered.connect(lambda: self.close())

        view_menu = QMenu("&View", self)
        menu_bar.addMenu(view_menu)
        search_action = QAction("&Search contacts", self)
        view_menu.addAction(search_action)
        search_action.setShortcut(QKeySequence.StandardKey.Find)
        search_action.triggered.connect(lambda: self.focus_search())

        options_menu = QMenu("&Options", self)
        menu_bar.addMenu(options_menu)
        self.database_location_action = QAction("", self)
        options_menu.addAction(self.database_location_action)
        self.database_location_action.setEnabled(False)
        change_database_action = QAction("Database &location...", self)
        options_menu.addAction(change_database_action)
        change_database_action.triggered.connect(
            lambda: self.choose_database_location()
        )
        self.restore_database_action = QAction("Use &default database", self)
        options_menu.addAction(self.restore_database_action)
        self.restore_database_action.triggered.connect(
            lambda: self.switch_database(DEFAULT_DB_PATH)
        )
        self.update_database_menu()

        help_menu = QMenu("&Help", self)
        menu_bar.addMenu(help_menu)
        about_action = QAction("&About Northstar", self)
        help_menu.addAction(about_action)
        about_action.triggered.connect(lambda: self.show_about())

    def update_database_menu(self) -> None:
        self.database_location_action.setText(f"Database: {DB_PATH.name}")
        self.database_location_action.setToolTip(str(DB_PATH))
        self.restore_database_action.setEnabled(
            DB_PATH.resolve() != DEFAULT_DB_PATH.resolve()
        )

    @staticmethod
    def validate_database(path: Path) -> None:
        if path.stat().st_size == 0:
            return

        encoded_path = quote(path.resolve().as_posix(), safe="/:")
        with closing(sqlite3.connect(f"file:{encoded_path}?mode=ro", uri=True)) as conn:
            tables = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            if "contacts" not in tables:
                raise ValueError("The selected database does not contain contacts.")
            columns = {row[1] for row in conn.execute("PRAGMA table_info(contacts)")}
            required_columns = {
                "id",
                "full_name",
                "title",
                "company",
                "role",
                "phone",
                "email",
                "category",
                "location",
                "linkedin",
                "github",
                "website",
                "notes",
            }
            missing_columns = required_columns - columns
            if missing_columns:
                missing = ", ".join(sorted(missing_columns))
                raise ValueError(
                    f"The selected contacts table is missing required columns: {missing}."
                )

    def choose_database_location(self) -> None:
        selected_path, _ = QFileDialog.getSaveFileName(
            self,
            "Choose database location",
            str(DB_PATH),
            "SQLite databases (*.db *.sqlite *.sqlite3)",
        )
        if selected_path:
            self.switch_database(Path(selected_path))

    def switch_database(self, path: Path) -> None:
        global DB_PATH
        new_path = path.expanduser().resolve()
        current_path = DB_PATH.resolve()
        if new_path == current_path:
            return
        if not new_path.parent.is_dir():
            QMessageBox.warning(
                self, "Database location unavailable", str(new_path.parent)
            )
            return

        if new_path.exists():
            try:
                self.validate_database(new_path)
            except (OSError, sqlite3.Error, ValueError) as error:
                QMessageBox.critical(
                    self,
                    "Unable to open database",
                    f"The selected file is not a valid contact database.\n\n{error}",
                )
                return

        answer = QMessageBox.question(
            self,
            "Change database",
            "Switch to this database? Any unsaved changes in the contact form will be discarded.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        previous_path = DB_PATH
        DB_PATH = new_path
        try:
            init_database(seed_if_empty=False)
        except (OSError, sqlite3.Error, ValueError) as error:
            DB_PATH = previous_path
            QMessageBox.critical(
                self,
                "Unable to open database",
                f"The database could not be initialized.\n\n{error}",
            )
            return

        settings = QSettings("Northstar", "Contact Book")
        if new_path == DEFAULT_DB_PATH.resolve():
            settings.remove(DATABASE_SETTINGS_KEY)
        else:
            settings.setValue(DATABASE_SETTINGS_KEY, str(new_path))
        self.selected_contact_id = None
        self.active_category_filter = "All categories"
        self.search_input.clear()
        self.clear_values()
        self.refresh_table(select_first=True)
        self.update_database_menu()
        status_bar = self.statusBar()
        if status_bar is None:
            raise RuntimeError("The application status bar is unavailable.")
        status_bar.showMessage(f"Database: {new_path}", 5000)

    def open_database_folder(self) -> None:
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(DB_PATH.parent))):
            QMessageBox.warning(
                self,
                "Unable to open folder",
                f"Could not open the database folder:\n{DB_PATH.parent}",
            )

    def show_about(self) -> None:
        QMessageBox.about(
            self,
            "About Northstar",
            f"<h3>Northstar Contact Book</h3>"
            f"<p>Your contacts are stored locally.</p>"
            f"<p><b>Database location</b><br>{html.escape(str(DB_PATH))}</p>",
        )

    @staticmethod
    def theme_stylesheet() -> str:
        return """
            QMainWindow, QWidget#mainArea { background: #f5f7fb; color: #17243a; }
            QMenuBar {
                background: #ffffff; color: #334258; border-bottom: 1px solid #e6ebf2;
                padding: 3px 8px;
            }
            QMenuBar::item { padding: 6px 10px; border-radius: 5px; }
            QMenuBar::item:selected { background: #edf2f7; }
            QMenu {
                background: #ffffff; color: #334258; border: 1px solid #e1e7ef;
                padding: 5px;
            }
            QMenu::item { padding: 7px 28px 7px 12px; border-radius: 4px; }
            QMenu::item:selected { background: #e8f5f3; color: #173a3a; }
            QFrame#sidebar { background: #111d33; }
            QLabel#brandMark {
                background: #2dd4bf; color: #102238; border-radius: 12px;
                font-size: 19px; font-weight: 800;
            }
            QLabel#brandName { color: #f8fafc; font-size: 16px; font-weight: 700; }
            QLabel#brandCaption { color: #91a0b7; font-size: 8px; font-weight: 700; letter-spacing: 1px; }
            QLabel#navigationCaption { color: #8290a8; font-size: 9px; font-weight: 700; padding: 5px 2px; }
            QPushButton#allContactsButton, QPushButton#groupNavigationButton {
                background: transparent; color: #c4cede; border: 0; border-radius: 8px;
                text-align: left; padding: 11px 12px; font-weight: 600;
            }
            QPushButton#allContactsButton:hover, QPushButton#groupNavigationButton:hover {
                background: #1d2b45; color: #ffffff;
            }
            QPushButton#allContactsButton:checked, QPushButton#groupNavigationButton:checked {
                background: #263650; color: #ffffff; border-left: 3px solid #2dd4bf;
            }
            QLabel#pageTitle { color: #15243b; font-size: 27px; font-weight: 750; }
            QLabel#pageSubtitle { color: #718096; font-size: 11px; }
            QPushButton#addContactButton, QPushButton#saveContactButton {
                background: #147d78; color: #ffffff; border: 0; border-radius: 8px;
                padding: 0 14px; min-height: 34px; font-weight: 700;
            }
            QPushButton#addContactButton:hover, QPushButton#saveContactButton:hover { background: #106b67; }
            QFrame#contactListCard, QFrame#detailsCard {
                background: #ffffff; border: 1px solid #e6ebf2; border-radius: 11px;
            }
            QLabel#listTitle { color: #1a2940; font-size: 14px; font-weight: 700; }
            QLabel#formSectionLabel {
                color: #748198; font-size: 9px; font-weight: 750;
                letter-spacing: 1px; padding-top: 5px; padding-bottom: 5px;
                border-bottom: 1px solid #edf0f5;
            }
            QLabel#formFieldLabel { color: #42526a; font-size: 10px; font-weight: 650; }
            QLabel#emptyStateLabel { color: #748198; padding: 18px; }
            QLabel#photoPreview {
                background: #f1f5f9; color: #8290a3; border: 1px dashed #d2dae5;
                border-radius: 12px;
            }
            QLabel#photoSectionTitle { color: #26364d; font-weight: 650; }
            QLabel#photoSectionHint { color: #8390a3; font-size: 9px; }
            QPushButton#choosePhotoButton, QPushButton#removePhotoButton {
                background: #f7f9fc; color: #42526a; border: 1px solid #dfe5ee;
                border-radius: 7px; padding: 0 10px; min-height: 32px;
                font-weight: 600;
            }
            QPushButton#choosePhotoButton:hover, QPushButton#removePhotoButton:hover {
                background: #edf2f7;
            }
            QPushButton#addPhoneButton, QPushButton#addEmailButton,
            QPushButton#addWebsiteButton, QPushButton#removePhoneButton,
            QPushButton#removeEmailButton, QPushButton#removeWebsiteButton {
                background: #f7f9fc; color: #42526a; border: 1px solid #dfe5ee;
                border-radius: 7px; padding: 0 9px; min-height: 28px;
                font-weight: 600;
            }
            QPushButton#addPhoneButton:hover, QPushButton#addEmailButton:hover,
            QPushButton#addWebsiteButton:hover, QPushButton#removePhoneButton:hover,
            QPushButton#removeEmailButton:hover, QPushButton#removeWebsiteButton:hover {
                background: #edf2f7;
            }
            QPushButton#removePhoneButton, QPushButton#removeEmailButton,
            QPushButton#removeWebsiteButton {
                color: #718096; font-size: 17px; padding: 0;
            }
            QPushButton#removePhoneButton:disabled, QPushButton#removeEmailButton:disabled,
            QPushButton#removeWebsiteButton:disabled {
                color: #cbd4e0; background: #fbfcfe;
            }
            QLineEdit, QComboBox, QTextEdit {
                background: #ffffff; color: #26364d; border: 1px solid #dfe5ee;
                border-radius: 7px; padding: 8px 10px; selection-background-color: #b7e5df;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus { border: 1px solid #17847d; }
            QComboBox { padding-right: 22px; }
            QPushButton#newContactButton, QPushButton#deleteContactButton {
                background: #f7f9fc; color: #42526a; border: 1px solid #dfe5ee;
                border-radius: 7px; padding: 0 12px; min-height: 32px;
                font-weight: 600;
            }
            QPushButton#newContactButton:hover { background: #edf2f7; }
            QPushButton#deleteContactButton { color: #b34444; border-color: #f1d9d9; }
            QPushButton#deleteContactButton:hover { background: #fff3f2; }
            QTableWidget {
                background: #ffffff; alternate-background-color: #fafbfd; border: 0;
                gridline-color: #edf0f5; color: #334258; selection-background-color: #e8f5f3;
                selection-color: #173a3a; outline: 0;
            }
            QHeaderView::section {
                background: #f8fafc; color: #7c899c; border: 0;
                border-bottom: 1px solid #e8edf3; padding: 10px 7px;
                font-size: 9px; font-weight: 700;
            }
            QScrollArea, QWidget#formScrollContents { background: #ffffff; }
            QScrollArea#groupNavigationScroll, QWidget#groupNavigationContent {
                background: transparent; border: 0;
            }
            QScrollBar:vertical { background: transparent; width: 8px; margin: 0; }
            QScrollBar::handle:vertical { background: #cbd4e0; border-radius: 4px; min-height: 25px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            QStatusBar { background: #f5f7fb; color: #718096; border: 0; }
        """

    def configure_table(self) -> None:
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ("Name", "Company", "Phone", "Email", "Websites", "Category")
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        vertical_header = self.table.verticalHeader()
        if vertical_header is None:
            raise RuntimeError("The contact table's vertical header is unavailable.")
        vertical_header.setVisible(False)
        vertical_header.setDefaultSectionSize(48)
        vertical_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header = self.table.horizontalHeader()
        if header is None:
            raise RuntimeError("The contact table's horizontal header is unavailable.")
        header.setMinimumSectionSize(64)
        for column in range(6):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)
        self.table.setIconSize(QSize(30, 30))
        self.table.setWordWrap(True)

    def configure_navigation(self) -> None:
        self.navigation_group = QButtonGroup(self)
        self.navigation_group.setExclusive(True)
        self.all_contacts_button = self.require_widget(QPushButton, "allContactsButton")
        self.group_navigation_layout = self.require_layout(
            QVBoxLayout, "groupNavigationLayout"
        )
        self.navigation_group.addButton(self.all_contacts_button)
        self.all_contacts_button.clicked.connect(
            lambda checked: (
                self.set_category_filter("All categories") if checked else None
            )
        )

    def refresh_category_controls(self) -> None:
        with closing(get_connection()) as conn:
            categories = [
                row["category"]
                for row in conn.execute(
                    """
                    SELECT DISTINCT TRIM(category) AS category
                    FROM contacts
                    WHERE category IS NOT NULL AND TRIM(category) != ''
                    ORDER BY category COLLATE NOCASE
                    """
                )
            ]

        selected_category = self.category.currentText()
        self.category.blockSignals(True)
        self.category.clear()
        self.category.addItems(categories)
        self.category.setEditText(selected_category)
        self.category.blockSignals(False)

        while self.group_navigation_layout.count():
            item = self.group_navigation_layout.takeAt(0)
            if item is None:
                raise RuntimeError("Could not remove a category navigation item.")
            widget = item.widget()
            if widget is not None:
                if isinstance(widget, QPushButton):
                    self.navigation_group.removeButton(widget)
                widget.deleteLater()

        active_filter = getattr(self, "active_category_filter", "All categories")
        self.all_contacts_button.setChecked(active_filter == "All categories")
        for category in categories:
            button = QPushButton(category)
            button.setObjectName("groupNavigationButton")
            button.setCheckable(True)
            button.setChecked(active_filter == category)
            self.navigation_group.addButton(button)
            button.clicked.connect(
                lambda _checked, value=category: (
                    self.set_category_filter(value) if _checked else None
                )
            )
            self.group_navigation_layout.addWidget(button)
        self.group_navigation_layout.addStretch()

    def connect_signals(self) -> None:
        self.table.itemSelectionChanged.connect(self.on_table_select)
        self.search_input.textChanged.connect(self.on_filter_changed)
        self.clear_search_shortcut = QShortcut(
            QKeySequence(Qt.Key.Key_Escape), self.search_input
        )
        self.clear_search_shortcut.activated.connect(self.search_input.clear)
        self.add_button.clicked.connect(self.create_new_contact)
        self.new_button.clicked.connect(self.create_new_contact)
        self.delete_button.clicked.connect(self.delete_selected_contact)
        self.save_button.clicked.connect(self.save_contact)
        self.choose_photo_button.clicked.connect(self.choose_contact_photo)
        self.remove_photo_button.clicked.connect(self.remove_contact_photo)
        self.add_phone_button.clicked.connect(
            lambda: self.add_contact_method_input("phone")
        )
        self.add_email_button.clicked.connect(
            lambda: self.add_contact_method_input("email")
        )
        self.add_website_button.clicked.connect(
            lambda: self.add_contact_method_input("website")
        )

    def focus_search(self) -> None:
        self.search_input.setFocus()
        self.search_input.selectAll()

    def add_contact_method_input(
        self, kind: str, value: str = "", focus: bool = False
    ) -> None:
        if kind == "phone":
            layout = self.phone_entries_layout
            inputs = self.phone_inputs
            remove_buttons = self.phone_remove_buttons
            placeholder = "Phone number"
        elif kind == "email":
            layout = self.email_entries_layout
            inputs = self.email_inputs
            remove_buttons = self.email_remove_buttons
            placeholder = "name@example.com"
        elif kind == "website":
            layout = self.website_entries_layout
            inputs = self.website_inputs
            remove_buttons = self.website_remove_buttons
            placeholder = "Website address"
        else:
            raise ValueError(f"Unsupported contact method: {kind}")

        row = QWidget(layout.parentWidget())
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)
        line_edit = QLineEdit(row)
        line_edit.setMinimumHeight(38)
        line_edit.setPlaceholderText(placeholder)
        line_edit.setText(value)
        remove_button = QPushButton("×", row)
        remove_button.setObjectName(f"remove{kind.title()}Button")
        remove_button.setAccessibleName(f"Remove {kind}")
        remove_button.setToolTip(f"Remove this {kind}")
        remove_button.setFixedSize(34, 38)
        remove_button.clicked.connect(
            lambda: self.remove_contact_method_input(kind, line_edit)
        )
        row_layout.addWidget(line_edit, 1)
        row_layout.addWidget(remove_button)
        layout.addWidget(row)
        inputs.append(line_edit)
        remove_buttons.append(remove_button)
        self.update_contact_method_remove_buttons(kind)
        if focus:
            line_edit.setFocus()

    def remove_contact_method_input(self, kind: str, field: QLineEdit) -> None:
        if kind == "phone":
            inputs = self.phone_inputs
            remove_buttons = self.phone_remove_buttons
            layout = self.phone_entries_layout
        elif kind == "website":
            inputs = self.website_inputs
            remove_buttons = self.website_remove_buttons
            layout = self.website_entries_layout
        elif kind == "email":
            inputs = self.email_inputs
            remove_buttons = self.email_remove_buttons
            layout = self.email_entries_layout
        else:
            raise ValueError(f"Unsupported contact method: {kind}")
        if len(inputs) <= 1:
            field.clear()
            return

        index = inputs.index(field)
        inputs.pop(index)
        remove_buttons.pop(index)
        row = field.parentWidget()
        if row is None:
            raise RuntimeError("The contact method input row is unavailable.")
        layout.removeWidget(row)
        row.deleteLater()
        self.update_contact_method_remove_buttons(kind)

    def update_contact_method_remove_buttons(self, kind: str) -> None:
        buttons = {
            "phone": self.phone_remove_buttons,
            "email": self.email_remove_buttons,
            "website": self.website_remove_buttons,
        }[kind]
        can_remove = len(buttons) > 1
        for button in buttons:
            button.setEnabled(can_remove)

    def set_contact_method_inputs(self, kind: str, values: Sequence[object]) -> None:
        if kind == "phone":
            layout = self.phone_entries_layout
            inputs = self.phone_inputs
            remove_buttons = self.phone_remove_buttons
        elif kind == "website":
            layout = self.website_entries_layout
            inputs = self.website_inputs
            remove_buttons = self.website_remove_buttons
        elif kind == "email":
            layout = self.email_entries_layout
            inputs = self.email_inputs
            remove_buttons = self.email_remove_buttons
        else:
            raise ValueError(f"Unsupported contact method: {kind}")

        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                raise RuntimeError("Could not remove a contact method input.")
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        inputs.clear()
        remove_buttons.clear()
        clean_values = [value for value in values if isinstance(value, str) and value]
        for value in clean_values or [""]:
            self.add_contact_method_input(kind, value)

    def contact_method_values(self, kind: str) -> list[str]:
        inputs = {
            "phone": self.phone_inputs,
            "email": self.email_inputs,
            "website": self.website_inputs,
        }[kind]
        values = [field.text().strip() for field in inputs]
        return [value for value in values if value]

    @staticmethod
    def save_contact_methods(
        conn: sqlite3.Connection, contact_id: int, kind: str, values: list[str]
    ) -> None:
        conn.execute(
            "DELETE FROM contact_methods WHERE contact_id = ? AND kind = ?",
            (contact_id, kind),
        )
        conn.executemany(
            """
            INSERT INTO contact_methods (contact_id, kind, position, value)
            VALUES (?, ?, ?, ?)
            """,
            [
                (contact_id, kind, position, value)
                for position, value in enumerate(values[1:], start=1)
            ],
        )

    def on_filter_changed(self) -> None:
        self.refresh_table()

    def set_category_filter(self, category: str) -> None:
        self.active_category_filter = category
        self.refresh_table()

    def contact_query(self) -> list[sqlite3.Row]:
        search_text = self.search_input.text().strip().casefold()
        category_filter = getattr(self, "active_category_filter", "All categories")
        query = """
            SELECT contacts.*,
                (
                    SELECT GROUP_CONCAT(value, char(10))
                    FROM (
                        SELECT value FROM contact_methods
                        WHERE contact_id = contacts.id AND kind = 'phone'
                        ORDER BY position
                    )
                ) AS additional_phones,
                (
                    SELECT GROUP_CONCAT(value, char(10))
                    FROM (
                        SELECT value FROM contact_methods
                        WHERE contact_id = contacts.id AND kind = 'email'
                        ORDER BY position
                    )
                ) AS additional_emails,
                (
                    SELECT GROUP_CONCAT(value, char(10))
                    FROM (
                        SELECT value FROM contact_methods
                        WHERE contact_id = contacts.id AND kind = 'website'
                        ORDER BY position
                    )
                ) AS additional_websites
            FROM contacts
            WHERE 1=1
        """
        params: list[str] = []

        if category_filter != "All categories":
            query += " AND category = ?"
            params.append(category_filter)

        if search_text:
            fields = (
                "full_name",
                "company",
                "role",
                "email",
                "title",
                "phone",
                "website",
                "location",
                "country",
                "category",
            )
            query += (
                " AND ("
                + " OR ".join(
                    f"LOWER(COALESCE({field}, '')) LIKE ?" for field in fields
                )
                + """
                    OR EXISTS (
                        SELECT 1 FROM contact_methods
                        WHERE contact_methods.contact_id = contacts.id
                            AND LOWER(contact_methods.value) LIKE ?
                    )
                )
                """
            )
            params.extend([f"%{search_text}%"] * (len(fields) + 1))

        query += " ORDER BY full_name COLLATE NOCASE ASC, id ASC"
        with closing(get_connection()) as conn:
            return conn.execute(query, params).fetchall()

    def refresh_table(self, select_first: bool = False) -> None:
        self.refresh_category_controls()
        previous_id = self.selected_contact_id
        rows = self.contact_query()
        self.table.blockSignals(True)
        self.table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            phone_values = [
                value for value in (row["phone"], row["additional_phones"]) if value
            ]
            email_values = [
                value for value in (row["email"], row["additional_emails"]) if value
            ]
            website_values = [
                value for value in (row["website"], row["additional_websites"]) if value
            ]
            values = (
                row["full_name"],
                row["company"],
                "\n".join(phone_values),
                "\n".join(email_values),
                "\n".join(website_values),
                row["category"],
            )
            for column_index, value in enumerate(values):
                item = QTableWidgetItem(str(value) if value else "-")
                if value:
                    item.setToolTip(str(value))
                if column_index == 0:
                    item.setData(Qt.ItemDataRole.UserRole, row["id"])
                    font = item.font()
                    font.setWeight(QFont.Weight.DemiBold)
                    item.setFont(font)
                    if row["photo"]:
                        pixmap = QPixmap()
                        if pixmap.loadFromData(row["photo"]):
                            item.setIcon(QIcon(pixmap))
                if column_index == 5:
                    item.setForeground(QColor("#24706b" if value else "#64748b"))
                self.table.setItem(row_index, column_index, item)
        self.table.resizeRowsToContents()

        self.table.blockSignals(False)
        self.empty_state.setVisible(not rows)
        self.table.setVisible(bool(rows))
        category = getattr(self, "active_category_filter", "All categories")
        self.list_title.setText(
            "All people" if category == "All categories" else f"{category} contacts"
        )

        target_row = None
        for index in range(self.table.rowCount()):
            item = self.table.item(index, 0)
            if item is not None and item.data(Qt.ItemDataRole.UserRole) == previous_id:
                target_row = index
                break
        if target_row is None and select_first and rows:
            target_row = 0
        if target_row is not None:
            self.table.selectRow(target_row)
            self.on_table_select()
        else:
            self.table.clearSelection()
            if previous_id is not None or not rows:
                self.selected_contact_id = None
                self.clear_values()

    def on_table_select(self) -> None:
        selection_model = self.table.selectionModel()
        if selection_model is None or not selection_model.hasSelection():
            return
        row_index = self.table.currentRow()
        if row_index < 0:
            return
        item = self.table.item(row_index, 0)
        if item is None:
            return
        contact_id = item.data(Qt.ItemDataRole.UserRole)
        if contact_id is None:
            return

        with closing(get_connection()) as conn:
            row_data = conn.execute(
                "SELECT * FROM contacts WHERE id = ?", (contact_id,)
            ).fetchone()
            phone_values = [
                row["value"]
                for row in conn.execute(
                    """
                    SELECT value FROM contact_methods
                    WHERE contact_id = ? AND kind = 'phone'
                    ORDER BY position
                    """,
                    (contact_id,),
                )
            ]
            website_values = [
                row["value"]
                for row in conn.execute(
                    """
                    SELECT value FROM contact_methods
                    WHERE contact_id = ? AND kind = 'website'
                    ORDER BY position
                    """,
                    (contact_id,),
                )
            ]
            email_values = [
                row["value"]
                for row in conn.execute(
                    """
                    SELECT value FROM contact_methods
                    WHERE contact_id = ? AND kind = 'email'
                    ORDER BY position
                    """,
                    (contact_id,),
                )
            ]
        if row_data is None:
            self.refresh_table()
            return

        self.selected_contact_id = int(contact_id)
        values = dict(row_data)
        values["phone_values"] = [
            value for value in (row_data["phone"], *phone_values) if value
        ]
        values["email_values"] = [
            value for value in (row_data["email"], *email_values) if value
        ]
        values["website_values"] = [
            value for value in (row_data["website"], *website_values) if value
        ]
        self.set_values(values)

    def get_values(self) -> dict[str, str]:
        first_name = self.first_name.text().strip()
        last_name = self.last_name.text().strip()
        phone_values = self.contact_method_values("phone")
        email_values = self.contact_method_values("email")
        website_values = self.contact_method_values("website")
        return {
            "full_name": f"{first_name} {last_name}".strip(),
            "first_name": first_name,
            "last_name": last_name,
            "title": self.title.text().strip(),
            "company": self.company.text().strip(),
            "role": self.role.text().strip(),
            "phone": phone_values[0] if phone_values else "",
            "email": email_values[0] if email_values else "",
            "category": self.category.currentText().strip(),
            "location": self.location.text().strip(),
            "country": self.country.text().strip(),
            "linkedin": self.linkedin.text().strip(),
            "github": self.github.text().strip(),
            "website": website_values[0] if website_values else "",
            "notes": self.notes.toPlainText().strip(),
        }

    def set_values(self, values: dict[str, object]) -> None:
        first_name = str(values.get("first_name") or "")
        last_name = str(values.get("last_name") or "")
        if not first_name and not last_name:
            first_name, last_name = split_full_name(str(values.get("full_name") or ""))
        self.first_name.setText(first_name)
        self.last_name.setText(last_name)
        self.title.setText(str(values.get("title") or ""))
        self.company.setText(str(values.get("company") or ""))
        self.role.setText(str(values.get("role") or ""))
        phone_values = values.get("phone_values")
        if not isinstance(phone_values, list):
            phone_values = [str(values.get("phone") or "")]
        self.set_contact_method_inputs("phone", phone_values)
        email_values = values.get("email_values")
        if not isinstance(email_values, list):
            email_values = [str(values.get("email") or "")]
        self.set_contact_method_inputs("email", email_values)
        self.category.setEditText(str(values.get("category") or ""))
        self.location.setText(str(values.get("location") or ""))
        self.country.setText(str(values.get("country") or ""))
        self.linkedin.setText(str(values.get("linkedin") or ""))
        self.github.setText(str(values.get("github") or ""))
        website_values = values.get("website_values")
        if not isinstance(website_values, list):
            website_values = [str(values.get("website") or "")]
        self.set_contact_method_inputs("website", website_values)
        self.notes.setPlainText(str(values.get("notes") or ""))
        photo = values.get("photo")
        self.contact_photo = photo if isinstance(photo, bytes) else None
        self.update_photo_preview()

    def update_photo_preview(self) -> None:
        pixmap = QPixmap()
        if self.contact_photo and pixmap.loadFromData(self.contact_photo):
            self.photo_preview.setPixmap(
                pixmap.scaled(
                    self.photo_preview.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            self.photo_preview.setText("")
        else:
            self.photo_preview.setPixmap(QPixmap())
            self.photo_preview.setText("No photo")
        self.remove_photo_button.setEnabled(self.contact_photo is not None)

    def choose_contact_photo(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose contact photo",
            str(Path.home()),
            "Images (*.png *.jpg *.jpeg *.webp *.bmp *.gif)",
        )
        if not file_path:
            return

        reader = QImageReader(file_path)
        reader.setAutoTransform(True)
        image_size = reader.size()
        if image_size.isValid():
            if (
                image_size.width() > 12000
                or image_size.height() > 12000
                or image_size.width() * image_size.height() > 40_000_000
            ):
                QMessageBox.warning(
                    self,
                    "Photo too large",
                    "Choose an image with no more than 40 megapixels.",
                )
                return
            reader.setScaledSize(
                image_size.scaled(QSize(512, 512), Qt.AspectRatioMode.KeepAspectRatio)
            )
        image = reader.read()
        if image.isNull():
            QMessageBox.warning(self, "Unable to load photo", reader.errorString())
            return

        buffer = QBuffer()
        if not buffer.open(QIODevice.OpenModeFlag.WriteOnly):
            QMessageBox.warning(
                self, "Unable to load photo", "Could not process the image."
            )
            return
        if not QPixmap.fromImage(image).save(buffer, "JPEG", 85):
            QMessageBox.warning(
                self, "Unable to load photo", "Could not encode the image."
            )
            return

        self.contact_photo = buffer.data().data()
        self.update_photo_preview()

    def remove_contact_photo(self) -> None:
        self.contact_photo = None
        self.update_photo_preview()

    def clear_values(self) -> None:
        self.contact_photo = None
        self.update_photo_preview()
        self.first_name.clear()
        self.last_name.clear()
        self.title.clear()
        self.company.clear()
        self.role.clear()
        self.set_contact_method_inputs("phone", [""])
        self.set_contact_method_inputs("email", [""])
        self.category.setEditText("")
        self.location.clear()
        self.country.clear()
        self.linkedin.clear()
        self.github.clear()
        self.set_contact_method_inputs("website", [""])
        self.notes.clear()

    def create_new_contact(self) -> None:
        self.selected_contact_id = None
        self.table.clearSelection()
        self.clear_values()
        self.first_name.setFocus()

    def save_contact(self) -> None:
        values = self.get_values()
        phone_values = self.contact_method_values("phone")
        email_values = self.contact_method_values("email")
        website_values = self.contact_method_values("website")
        values["phone"] = phone_values[0] if phone_values else ""
        values["email"] = email_values[0] if email_values else ""
        values["website"] = website_values[0] if website_values else ""
        missing_fields = [
            label
            for key, label in (
                ("first_name", "First name"),
                ("last_name", "Last name"),
                ("country", "Country"),
            )
            if not values[key]
        ]
        if missing_fields:
            if len(missing_fields) == 1:
                missing_text = missing_fields[0]
            elif len(missing_fields) == 2:
                missing_text = " and ".join(missing_fields)
            else:
                missing_text = (
                    f"{', '.join(missing_fields[:-1])}, and {missing_fields[-1]}"
                )
            QMessageBox.warning(
                self,
                "Missing required information",
                f"{missing_text} {'are' if len(missing_fields) > 1 else 'is'} required.",
            )
            missing_key = next(
                key for key in ("first_name", "last_name", "country") if not values[key]
            )
            {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "country": self.country,
            }[missing_key].setFocus()
            return

        with closing(get_connection()) as conn:
            if self.selected_contact_id is None:
                cursor = conn.execute(
                    """
                    INSERT INTO contacts (
                        full_name, first_name, last_name, title, company, role, phone, email,
                        category, location, country, linkedin, github, website, notes, photo
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        values["full_name"],
                        values["first_name"],
                        values["last_name"],
                        values["title"],
                        values["company"],
                        values["role"],
                        values["phone"],
                        values["email"],
                        values["category"],
                        values["location"],
                        values["country"],
                        values["linkedin"],
                        values["github"],
                        values["website"],
                        values["notes"],
                        self.contact_photo,
                    ),
                )
                saved_contact_id = cursor.lastrowid
                if saved_contact_id is None:
                    raise RuntimeError("Could not determine the new contact ID.")
            else:
                conn.execute(
                    """
                    UPDATE contacts SET
                        full_name = ?, first_name = ?, last_name = ?, title = ?, company = ?,
                        role = ?, phone = ?, email = ?, category = ?, location = ?, country = ?,
                        linkedin = ?, github = ?, website = ?, notes = ?, photo = ?
                    WHERE id = ?
                    """,
                    (
                        values["full_name"],
                        values["first_name"],
                        values["last_name"],
                        values["title"],
                        values["company"],
                        values["role"],
                        values["phone"],
                        values["email"],
                        values["category"],
                        values["location"],
                        values["country"],
                        values["linkedin"],
                        values["github"],
                        values["website"],
                        values["notes"],
                        self.contact_photo,
                        self.selected_contact_id,
                    ),
                )
                saved_contact_id = self.selected_contact_id
            self.save_contact_methods(conn, saved_contact_id, "phone", phone_values)
            self.save_contact_methods(conn, saved_contact_id, "email", email_values)
            self.save_contact_methods(conn, saved_contact_id, "website", website_values)
            conn.commit()

        self.selected_contact_id = saved_contact_id
        self.refresh_table()
        status_bar = self.statusBar()
        if status_bar is None:
            raise RuntimeError("The application status bar is unavailable.")
        status_bar.showMessage("Contact saved.", 3000)

    def delete_selected_contact(self) -> None:
        if self.selected_contact_id is None:
            QMessageBox.information(
                self, "No selection", "Select a contact before deleting."
            )
            return

        confirmation = QMessageBox.question(
            self,
            "Delete contact",
            "Delete this contact? This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirmation != QMessageBox.StandardButton.Yes:
            return

        with closing(get_connection()) as conn:
            conn.execute(
                "DELETE FROM contacts WHERE id = ?", (self.selected_contact_id,)
            )
            conn.commit()

        self.selected_contact_id = None
        self.clear_values()
        self.refresh_table(select_first=True)
        status_bar = self.statusBar()
        if status_bar is None:
            raise RuntimeError("The application status bar is unavailable.")
        status_bar.showMessage("Contact deleted.", 3000)


def main() -> None:
    app = QApplication([])
    app.setOrganizationName("Northstar")
    app.setApplicationName("Contact Book")
    app.setStyle("Fusion")

    global DB_PATH
    settings = QSettings("Northstar", "Contact Book")
    configured_path = settings.value(DATABASE_SETTINGS_KEY, "", type=str)
    if configured_path:
        DB_PATH = Path(configured_path).expanduser().resolve()
        if not DB_PATH.is_file():
            QMessageBox.warning(
                None,
                "Database not found",
                f"The configured database could not be found:\n{DB_PATH}\n\n"
                "Choose another database location to continue.",
            )
            selected_path, _ = QFileDialog.getSaveFileName(
                None,
                "Choose database location",
                str(DEFAULT_DB_PATH),
                "SQLite databases (*.db *.sqlite *.sqlite3)",
            )
            if not selected_path:
                return
            DB_PATH = Path(selected_path).expanduser().resolve()
    else:
        DB_PATH = DEFAULT_DB_PATH

    try:
        if DB_PATH.exists():
            ContactBookWindow.validate_database(DB_PATH)
        init_database(seed_if_empty=DB_PATH.resolve() == DEFAULT_DB_PATH.resolve())
    except (OSError, sqlite3.Error, ValueError) as error:
        QMessageBox.critical(
            None,
            "Unable to open database",
            f"The contact database could not be opened:\n{DB_PATH}\n\n{error}",
        )
        return

    if configured_path and not Path(configured_path).expanduser().resolve().is_file():
        if DB_PATH.resolve() == DEFAULT_DB_PATH.resolve():
            settings.remove(DATABASE_SETTINGS_KEY)
        else:
            settings.setValue(DATABASE_SETTINGS_KEY, str(DB_PATH))

    window = ContactBookWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
