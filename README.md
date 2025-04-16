![BizTrack_Logo](https://github.com/user-attachments/assets/76f56ee6-66a0-4a0e-b56e-a7ecbd222cd5)


<h1>Biztrack</h1>
<h3>BizTrack is a full-stack web application designed for business owners to efficiently manage their operations. This repository houses the frontend of the BizTrack application, built with React and TypeScript.</h3>

<br />
<br />

<h2>✨ Features</h2>
<ul>
  <li>
    <h3><b>JWT Authentication:</b> Secure user authentication with refresh and access tokens via Djoser.</h3>
  </li>
  <li>
    <h3><b>Product Management:</b> CRUD APIs to manage product listings.</h3>
  </li>
  <li>
    <h3><b>Customer Management:</b> Keep track of customer contact details and sales history</h3>
  </li>
  
  <li>
    <h3><b>Sales Tracking:</b> API endpoints to analyze performance metrics.</h3>
  </li>
  <li>
    <h3><b>User Scoped Data:</b> Each user can only access their own data (products, customers, invoices).</h3>
  </li>
  <li>
    <h3><b>DRF ViewSets and Serializers:</b> Clean, modular API structure with proper permissions.</h3>
  </li>
</ul>

<br />

<h2>🛠️ Tech Stack</h2>

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#)
[![Django](https://img.shields.io/badge/Django-%23092E20.svg?logo=django&logoColor=white)](#)
[![DjangoREST](https://img.shields.io/badge/Django%20REST-ff1709?logo=django&logoColor=white&color=ff1709)](#)
[![Postgres](https://img.shields.io/badge/Postgres-%23316192.svg?logo=postgresql&logoColor=white)](#)

<ul>
  <h3><li><b>Backend:</b> Django, Django REST Framework</li></h3>
  <h3><li><b>Authentication:</b> Djoser + JWT (Simple JWT)</li></h3>
  <h3><li><b>Database:</b> PostgreSQL</li></h3>
</ul>

<br />

<h2>📡 REST API Endpoints</h2>

All APIs follow REST principles and return JSON responses. Below are some core routes:

| Method | Endpoint             | Description                  |
|--------|----------------------|------------------------------|
| POST   | `/auth/jwt/create/`  | Get JWT tokens (login)       |
| POST   | `/auth/users/`       | Register new user            |
| GET    | `/api/products/`     | List all user products       |
| POST   | `/api/invoices/`     | Create a new invoice         |
| GET    | `/api/customers/`    | View or manage customers     |
| GET    | `/api/dashboard/`    | *(Optional)* View business summary |


> All endpoints require a JWT token in the `Authorization` header unless marked public.


<br />

<h2>🔒 Authentication</h2>

<ul>
  <li><h3>Uses JWT (JSON Web Tokens) via SimpleJWT and Djoser.</h3></li>
  
  <li><h3>Tokens returned on login:</h3></li>
    <ul>
        <li><h4>access: short-lived token for API access</h4></li>
        <li><h4>refresh: used to obtain new access token</h4></li>
    </ul>
    
  <li><h3>You can store these tokens securely in local storage or use HttpOnly cookies for better protection against XSS.</h3></li>
</ul>

<br />

<h2>🧪 Local Development</h2>

<h3>1. Clone the repository:</h3>

```bash
git clone https://github.com/sikatanju/biztrack-backend.git
```
<h3>2. Navigate to the project directory:</h3>

```bash
cd biztrack-backend
```
<h3>3. Create a virtual environment and activate it:</h3>

```bash
python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
```
<h3>4. Install the dependencies:</h3>

```bash
pip install -r requirements.txt
```
<h3>5. Apply migrations and run the development server:</h3>

```bash
python manage.py migrate
python manage.py runserver
```

<br />


<h2>🔮 Future Improvements</h2>

<h3><b>1. Swagger/OpenAPI:</b> docs for easier API testing and visualization.</h3>
<h3><b>2. Unit & integration tests:</b> with pytest or DRF's built-in test client.</h3>
<h3><b>3. Pagination and filtering:</b> for all endpoints.</h3>
<h3><b>4. Rate Limiting & Throttling:</b> for enhanced API protection.</h3>

<br />

<h2>📱 Screenshots</h2>

![chrome_hUAAH1VEqU](https://github.com/user-attachments/assets/481182ab-fabc-4fe9-b655-4ed468039fea)

<br />

![chrome_EwICUjCIvP](https://github.com/user-attachments/assets/e6a51339-fdc1-47e4-8fd1-b5c00d3e6484)

<br />

![chrome_eV656ihbBU](https://github.com/user-attachments/assets/bd8a12fa-99e2-4649-8223-77da3c05a218)

<br />

![chrome_TFFiYkwf4i](https://github.com/user-attachments/assets/ca6fadcf-bd12-4959-8fcb-99f1c1ca5027)

<br />


<h2>🤝 Contributing</h2>

<h3>Contributions are welcome! Please feel free to submit a Pull Request.</h3>

<h3>1. Fork the project</p> 
<h3>2. Create your feature branch (git checkout -b feature/AmazingFeature)</p> 
<h3>3. Commit your changes (git commit -m 'Add some AmazingFeature')</p> 
<h3>4. Push to the branch (git push origin feature/AmazingFeature)</p> 
<h3>5. Open a Pull Request</p> 

<br />

<h2>📝 License</h2>

<h3>This project is licensed under the MIT License - see the LICENSE file for details.</p> 

