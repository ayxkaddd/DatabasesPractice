# практика з баз даних

## database structure

![altlttllt](https://ayxdacat.lol/i/X7t5ur29.png)

```sql
CREATE TABLE Categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE Menu_Items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id)
);

CREATE TABLE Customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL
);

CREATE TABLE Orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    order_date DATETIME NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);

CREATE TABLE Order_Items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    item_id INT,
    quantity INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (item_id) REFERENCES Menu_Items(item_id)
);

CREATE TABLE Employees (
	employee_id INT AUTO_INCREMENT PRIMARY KEY,
	first_name VARCHAR(50) NOT NULL,
	last_name VARCHAR(50) NOT NULL,
	employee_code INT(4) UNIQUE NOT NULL
);

CREATE TABLE Credentials (
    employee_id INT PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES Employees(employee_id)
);
```

## file structure

```
├── main.py (main file, handles templates and includes routes)
├── auth.py (JWT auth logic)
├── helpers.py (helper functions for database)
├── models.py (pydantic models for api)
├── routes (all of the api routes included in main)
│   ├── auth_routes.py
│   ├── category_routes.py
│   ├── customer_routes.py
│   ├── employee_routes.py
│   ├── image_routes.py
│   ├── menu_routes.py
│   ├── order_routes.py
│   └── report_routes.py
├── static (templates folder)
│   ├── css
│   │   └── style.css
│   ├── images
│   │   ├── cash_icon.png
│   │   └── credit_card_icon.png
│   ├── js
│   │   ├── api.js
│   │   ├── auth.js
│   │   ├── categories.js
│   │   ├── customers.js
│   │   ├── employees.js
│   │   ├── graphs.js
│   │   ├── main.js
│   │   ├── menuItems.js
│   │   ├── orders.js
│   │   ├── ui.js
│   │   └── utils.js
│   ├── dashboard.html
│   ├── index.html
│   └── login.html
```

## tech stack

### backend
- Python: Core programming language.
- FastAPI: Web framework for building APIs.
- MySQL: Relational database management system.

### frontend
- HTML5: Markup language for creating the structure of the web pages.
- CSS3: Style sheet language for designing the web pages.
- JavaScript: Programming language for creating interactive and dynamic content on web pages.
- Chart.js: JavaScript library for creating beautiful and interactive charts.

### tools & libraries
- Pydantic: Data validation and settings management using Python type annotations.
- mysql-connector-python: MySQL database connector for Python.
- Jinja2: Template engine for Python.
