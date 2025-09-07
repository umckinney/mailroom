# Mailroom

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/umckinney/mailroom/actions)

Mailroom is an object-oriented Python application that manages a donor database for a charitable organization. It allows users to track donations, generate reports, and send thank-you messages — all from the command line.

This version reflects a refactored final implementation from a multi-week learning project. It emphasizes clean class design, test coverage, and modular structure.

---

## 🧰 Features

- Add new donors and donations
- Automatically update donor statistics (total, count, average)
- Generate reports summarizing donor activity
- Send thank-you notes
- Deactivate donors
- Input validation
- Pagination logic (stretch feature)

---

## 🗂 Project Structure

```bash
mailroom/               # Main application code
  ├── __init__.py
  ├── mailroom_model.py
  ├── main.py
  └── templates.py      # Thank-you note templates

tests/                  # Pytest unit tests
  └── test_mailroom_model.py

README.md               # This file
pyproject.toml          # Project metadata & test config
.gitignore              # Ignored files and folders
```

---

## 🚀 Getting Started

### 🧱 Requirements

- Python 3.12+
- [pip](https://pip.pypa.io/en/stable/installation/)

### 📦 Install Dependencies (if any)

This project currently has no external dependencies. If future requirements are added, they’ll be managed via `pyproject.toml`.

### 🧪 Run Tests

```bash
cd mailroom
pytest
```

Or run explicitly from the `tests/` directory:

```bash
cd tests
pytest test_mailroom_model.py
```

---

## 📸 Sample Output

```
| Email             | First Name | Last Name | Total Given | Gifts | Average Gift |
|------------------|------------|-----------|-------------|-------|----------------|
| test@donor.com   | Test       | Donor     | $300.00     | 3     | $100.00       |
```

---

## 📃 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙋 Author

**Uriah McKinney**  
🔗 [GitHub: umckinney](https://github.com/umckinney)
