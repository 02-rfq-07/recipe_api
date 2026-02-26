# 🍽 Recipe API 

## Overview

This repo demonstrates a backend API that parses a large JSON dataset of recipes, stores it in a MySQL database, and provides APIs for searching, filtering, pagination, and sorting.

It is designed to handle large-scale data efficiently. it handles cleaning, parsing along with preprocessing of the dataset.

---

## Tech Stack

* Python (Flask)
* MySQL (Database)
* JSON processing
* REST APIs

---

## Implementation Logic:
### 1. JSON Parsing

The dataset is provided in JSON format where recipes are stored as key-value pairs:
```json
{
  "0": {...},
  "1": {...}
}
```
we iterate over the values by:

```python
for item in data.values():
```
and retrieve each recipe object.

---

### 2. Data Cleaning

The dataset contains:

* `NaN`
* Empty strings
* Missing values
These cases are handled before insertion:
```python
def clean_value(value):
    if value in ["NaN", "", None]:
        return None
    return value
```

---

### 3. Handling Complex Fields

####  Nutrients (JSON field)

The nutrients field is stored as JSON in MySQL:

```python
nutrients = json.dumps(item.get("nutrients"))
```

---

#### 📌 Calories Extraction

Calories are stored as strings like:

```
"389 kcal"
```

To enable filtering, numeric values are extracted at query time:

```sql
CAST(
  REGEXP_SUBSTR(
    JSON_UNQUOTE(JSON_EXTRACT(nutrients, '$.calories')),
    '[0-9]+'
  ) AS UNSIGNED
)
```
REGEXP_SYBSTR - extract substring from string using regular expression.
JSON_UNQUOTE - remove quotes from the string.
JSON_EXTRACT - extract specific data.
CAST - convert the input to required datatye.
---

### 4. Batch Insertion

To efficiently handle large datasets, batch insertion is used:

```python
cursor.executemany(query, batch)
```

* Reduces database calls
* Improves performance
* Handles large datasets efficiently

---

### 5. Database Design

* Relational schema used for structured fields
* JSON column used for flexible nutrient storage

This hybrid approach balances:

* Performance
* Flexibility

---


## Features

* Parse large JSON dataset
* Batch insertion into database
* Handles missing/NaN values
* Pagination & sorting
* Dynamic filtering:

  * Title (LIKE)
  * Cuisine (LIKE)
  * Rating (>, <, >=, <=)
  * Total time
  * Calories (parsed from JSON)

---

## Database Schema
 _ _ _ _ _ _ _ _ _ _ _ _ 
| Column      | Type     |
| ----------- | -------- |
| id          | INT (PK) |
| title       | VARCHAR  |
| cuisine     | VARCHAR  |
| rating      | FLOAT    |
| prep_time   | INT      |
| cook_time   | INT      |
| total_time  | INT      |
| description | TEXT     |
| nutrients   | JSON     |
| serves      | VARCHAR  |
|_ _ _ _ _ _ _ _ _ _ _ _ |
---

## Setup Instructions

### 1. Clone the repository

```
git clone https://github.com/02-rfq-07/recipe_api.git
cd recipe-api
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

### 3. Configure MySQL

Update credentials in `app.py`:

```
host="localhost"
user="root"
password="your_password"
```

### 4. Initialize DB

To intitialize the database uncomment and run app.py:
```
init_db()
```

### 5. Load Data

To load the data into the database, uncomment and run app.py:
```
load_data()
```

### 6. Run server

```
python app.py
```

---

##  API Endpoints (Examples)

### -> Get Recipes (Pagination)

```
GET /api/recipes?page=1&limit=10
```

### -> Search Recipes

```
GET /api/recipes/search?title=pasta&rating=>=4.5&calories<=400
```

---

## Design Decisions

* **Batch insert** used for handling large datasets efficiently
* **JSON column** used for flexible nutrient storage
* **REGEXP + CAST** used to extract numeric values from calorie strings
* **Parameterized queries** used to prevent SQL injection
* **Dynamic query building** using `1=1` for flexibility

---



## 👨‍💻 Author

Mohammad Rafeeq S
