Below are example configurations for various connectors. Each configuration is formatted as a Python dictionary for easy copying.

# ODBC connector példa:
Ezt a connectort service user-es használatra szabtuk.

```python
odbc_config = {
    "DRIVER": "ODBC Driver 17 for SQL Server",
    "SERVER": "localhost",
    "DATABASE": "test_db",
    "UID": "felhasználónév",
    "PWD": "jelszó",
    "TRUSTED_CONNECTION": False  # Opcionális, Windows-hitelesítéshez
}
```

# SQLite connector config félda
Az SQLite connector csak egy file path-t vár a db eléréhez, local fejlesztésre van szabva. 

```python
sqlite_config = {
    "DATABASE": "path/to/test_db.sqlite",
}
```