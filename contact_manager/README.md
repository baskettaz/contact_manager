# Northstar Contact Book

A local-first PyQt6 contact manager with searchable contacts, contact details,
notes, optional photos, and SQLite persistence.

## Run

From the project root, sync dependencies from `pyproject.toml` and start the
application:

```powershell
uv sync
uv run python contact_manager/gui/contact_book_app.py
```

`contact_book.ui` is loaded at runtime from the same directory as the
application. Keep both files together when moving or packaging it. By default,
contact data is stored in `contact_book.db` beside the app.

Use **Options > Database location...** to choose or create a SQLite database.
The selected location is saved in your user settings and reused the next time
the app starts. Use **Options > Use default database** to switch back. The
current location is also shown in the Options menu.

First name, last name, and country are required to save a contact. Existing
contacts are split into first and last names and locations into city and
country when the database is upgraded.

Categories are shown in the sidebar and contact list. Choose a category in the
sidebar to filter contacts, or type a new category in the contact editor. The
search bar remains a text-only search.

The contact editor groups personal, work, contact, location, and online details
into sections. Add multiple phone numbers, email addresses, or websites with
the inline Add buttons. Every saved number, address, and website is shown in
the contacts overview and remains searchable.

Contact photos are optional. Choose a photo in the contact editor and save the
contact to store it in the local database; images are resized to fit within
512 x 512 pixels, so the original image file does not need to stay in place.
