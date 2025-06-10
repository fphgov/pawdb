# **PawDB Dokumentáció**

## **Áttekintés**
A PawDB célja, hogy egyszerű és egységes interfészt biztosítson különböző típusú adatbázisok kezeléséhez. Egyszerűsíti az adatbázis-műveleteket, például a csatlakozást, lekérdezések végrehajtását és az eredmények lekérését, miközben támogatja a naplózást és a teljesítményfigyelést.

A könyvtár moduláris kialakítású, így a fejlesztők könnyen cserélhetik az adatbázis connectorokat különböző környezetekhez (pl. dev/prod).

#### Jelenleg támogatott adatbázisok
- MSSQL Server (pyodbc)
- SQLite

---

## **Telepítés**

A Python verzió rögzített (>=3.10,<3.11) az Airflow kompatibilitás miatt.
A pawdb működését nem feltételn zavarja ha egy projekt eltér ettől, de a további függőségeket ehhez igazítottuk,
és a package-et így teszteltük.

### **Poetry (recommended)**
```bash
poetry add git+https://github.com/fphgov/pawdb.git#master
```

### **PIP**
```bash
pip install git+https://github.com/fphgov/pawdb.git@master
```


## **Használat**

### **1. Konfiguráció**
A package különböző connectorokat tartalmaz, amik más-más adatbázisokhoz való csatlakozást kezelnek.
Minden csatlakozó egy konfigurációs szótárat vár, amiben a szükséges kulcsok az adatbázis és connector típusától függnek.


#### **Példa konfiguráció SQL Serverhez (ODBCConnector)**
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
A további adatbázisok config igényeit lásd a [configs](configs.md) oldalon!



---

### **2. Kapcsolódás egy adatbázishoz**
Használd a megfelelő csatlakozó osztályt (pl. `ODBCConnector` vagy `SQLiteConnector`) a kapcsolat létrehozásához.

#### **SQL Server példa**
```python
from pawdb.connectors.odbc import ODBCConnector

connector = ODBCConnector(odbc_config)
connector.connect()
```

#### **SQLite példa**
```python
from pawdb.connectors.sqlite import SQLiteConnector

config = {"DATABASE": "test.db"}
connector = SQLiteConnector(config)
connector.connect()
```

---

### **3. Lekérdezések végrehajtása**
Az interfész különböző módszereket biztosít a lekérdezések végrehajtására és az eredmények lekérésére.

#### **Query végrehajtása**
```python
connector.execute_query("CREATE TABLE users (id INTEGER, name TEXT)")
connector.execute_query("INSERT INTO users (id, name) VALUES (?, ?)", params=(1, "Alice"))
```

#### **Eredmények lekérése listaként**
```python
results = connector.fetch_query_to_list("SELECT * FROM users")
print(results["data"])  # [(1, 'Alice')]
```

#### **Eredmények lekérése Pandas DataFrame-ként**
```python
df = connector.fetch_query_to_pandas("SELECT * FROM users")
print(df["data"])
```

#### **Kapcsolat bezárása**
```python
connector.close()
```

---

## **Interfész**

Az alábbi metódusok minden csatlakozóban implementálva vannak (`ODBCConnector` és `SQLiteConnector`):

| Metódus                     | Leírás                                                                 |
|-----------------------------|-------------------------------------------------------------------------|
| `connect()`                 | Kapcsolat létrehozása az adatbázissal.                                 |
| `close()`                   | Az adatbázis-kapcsolat és kurzor bezárása.                             |
| `execute_query(query, params=None)` | Lekérdezés végrehajtása eredmények visszaadása nélkül.                     |
| `fetch_query_to_list(query, params=None)` | Lekérdezés végrehajtása és eredmények lekérése tuple-listaként.         |
| `fetch_query_to_pandas(query, params=None)` | Lekérdezés végrehajtása és eredmények lekérése Pandas DataFrame-ként. |

---

## **Naplózás**
A PawDB strukturált naplózást biztosít a `python-json-logger` segítségével. A naplók tartalmazzák:
- A metódus nevét
- A végrehajtott lekérdezést
- Az érintett vagy lekért sorok számát
- A végrehajtási időt

### **Példa naplóbejegyzés**
```json
{
  "asctime": "2025-06-10T12:34:56",
  "name": "pawdb",
  "levelname": "INFO",
  "message": "Lekérdezés sikeresen végrehajtva.",
  "method": "pawdb.connectors.odbc.ODBCConnector.execute_query",
  "query": "SELECT * FROM users",
  "rows_affected": 1,
  "execution_time": "0.12s"
}
```
---

## **Fejlesztés és tesztelés**

### **Mocking SQLite-tal**
Fejlesztés során az `SQLiteConnector` használható a produkciós adatbázisok helyettesítésére. Ez lehetővé teszi az alkalmazás tesztelését anélkül, hogy hozzáférésre lenne szükség egy éles adatbázishoz.

### **Unittesting**
Az `SQLiteConnector` segítségével ideiglenes memóriában lévő adatbázisok hozhatók létre egységtesztekhez:
```python
from pawdb.connectors.sqlite import SQLiteConnector

def test_database_operations():
    config = {"DATABASE": ":memory:"}  # Memóriában lévő SQLite adatbázis
    connector = SQLiteConnector(config)
    connector.connect()
    connector.execute_query("CREATE TABLE users (id INTEGER, name TEXT)")
    connector.execute_query("INSERT INTO users (id, name) VALUES (?, ?)", params=(1, "Alice"))
    results = connector.fetch_query_to_list("SELECT * FROM users")
    assert results["data"] == [(1, "Alice")]
    connector.close()
```
