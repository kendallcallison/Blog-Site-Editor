# 📝 Blog Post Manager

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![GUI](https://img.shields.io/badge/GUI-Tkinter-yellow)
![SFTP](https://img.shields.io/badge/SFTP-Enabled-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

A desktop app to remotely manage blog posts on a server using Python, Tkinter, and SFTP. Supports creating, uploading, and deleting blog posts with metadata and image support.

---

## 🚀 Features

- 🔒 Secure SFTP integration (via `paramiko`)
- ✍️ Add rich blog posts with images and metadata
- 📂 Automatically updates `meta.json` post index
- ❌ Delete old posts with confirmation
- 🖼️ GUI-based interface for ease of use

---

## ⚙️ Prerequisites

### Python Installation

**Windows:**
- Download from [python.org](https://www.python.org/downloads/)
- ✅ Be sure to check **"Add Python to PATH"**

**macOS (Homebrew):**
```bash
brew install python3
```
**Linux (Debian/Ubuntu):**

```
sudo apt update
sudo apt install python3 python3-pip
```
## 📦 Setup Instructions
Clone this repository or download the files.

Install required libraries:

```
pip install paramiko beautifulsoup4
```
Create a config.txt file in the root directory:

```
hostname=your.sftp.server.com
port=22
username=your_username
password=your_password
publicFilePath=/path/to/your/webroot/
```

## 🖥️ Running the App

```
python3 blogUI.py
```
A window will open listing existing blog posts.

You can add or remove blog posts using the buttons.

## 📁 Server File Structure
```
/your/publicFilePath/
├── index.html
├── styles.css
├── posts/
│   ├── meta.json
│   ├── post_*.html
├── images/
│   ├── uploaded_images.jpg
```
Blog post metadata is stored in posts/meta.json

Blog content is stored as individual HTML files

Images are stored in the images/ folder
