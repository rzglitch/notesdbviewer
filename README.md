# Notes DB Viewer

This is code designed to view the database of a Notes app for the world's second largest mobile operating system.

Implemented the following features:

* Notes list
* View note contents
* Show attachments

TODO:

* Parsing of elements such as links, tables, etc.
* More specific WYSIWYG implementation

## Requirements

* Python 3.8 or later, with Flask installed.
* Notes stored on their public cloud storage must be moved to your device before extracting the database.

## File structure

```
AppDomainGroup-group.com.apple.notes/
  - Accounts/
    - LocalAccount/
      - FallbackImages/
      - Media/
      - Paper/
      - Previews/
  - NoteStore.sqlite
```

## Run

```sh
$ pip install flask
$ flask --app viewer run
```

## Legal

Copyright © 2023 rzglitch

**Disclaimer: This tool enables view the contents of the Notes app database extracted from the device. This tool should ONLY be used with backups extracted from your own device or with the owner's consent of device from which the backup originates. Never use this tool for any illegal purpose.**

**The project contributors are not responsible if criminal charges are brought against any person or entity that breaks the law by misusing this tool and/or the information it contains.**
