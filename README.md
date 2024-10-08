# Transparent Encryption Intermediate Layer

This repository contains two approaches for implementing an intermediate layer for transparent encryption in PostgreSQL, aimed at securing sensitive data. Each approach handles encryption and decryption operations either through a command-line interface or via a REST API.

## Project Structure

### 1. IntLayer_cmdMenu (Command-Line Menu Based)
This folder contains the visual, menu-based prototype of the intermediate layer, designed for user interaction. It includes the following files:

- **login.py**: Handles user authentication and authorization (login and signup).
- **encryption.py**: Manages encryption decryption of data.
- **decryption.py**: Manages decryption decryption of data.
- **crud.py**: Allows the user to perform Create, Read, Update, and Delete operations on the database.
- **EDEsim.py**: The main script that ties together the login/signup process, encryption, decryption and CRUD operations.

### 2. IntLayer_RestAPI (REST API Based)
This folder contains the REST API version of the intermediate layer, built using FastAPI. It adapts the first approach by providing API endpoints to handle encryption, decryption, and CRUD operations programmatically.

- **encryption.py**: Handles insertion of encrypted data.
- **decryption.py**: Handles decryption per row, using an id for selection.
- **crud.py**: Manages database operations via API calls.
- **EDEsim.py**: The main FastAPI application that exposes endpoints for login, signup, encryption, decryption, and CRUD operations.
