
# Domator Product Catalog

A full-stack web application for managing and displaying products, built with **React** (frontend), **Flask** (backend), and **PostgreSQL** (database). The app is designed for a home products store, with an admin panel for product management and a public-facing product catalog.

## Features

- **Product Catalog**: Responsive grid of products with images, prices, and descriptions.
- **Product Images**: Upload and display product images (stored in the database).
- **Admin Panel**:
	- Add, edit, and delete products.
	- Set product price, description, category, and optional Ceneo comparison link.
	- Login required for admin access.
- **Ceneo Integration**: If a product has a Ceneo link, a "Porównaj z Ceneo" button appears on the product card, opening the link in a new tab.
- **Info/Contact Modal**: Accessible from the home page.
- **Password Reset UI**: (Frontend only, backend logic can be added).
- **Modern UI**: Uses Bootstrap for responsive design and custom CSS for branding.

## Tech Stack

- **Frontend**: React, Vite, Bootstrap, custom CSS
- **Backend**: Flask, psycopg2 (PostgreSQL)
- **Database**: PostgreSQL
- **Other**: Supabase client (optional), ESLint for code quality

## Project Structure

```
├── src/
│   ├── app.py                # Flask backend
│   ├── components/           # React components
│   ├── pages/                # React pages
│   ├── styles/               # CSS files
│   └── assets/               # Images and static assets
├── Dockerfile.backend        # Docker config for backend
├── Dockerfile.frontend       # Docker config for frontend
├── docker-compose.yml        # Orchestration
├── package.json              # Frontend dependencies
├── requirements.txt          # Backend dependencies
└── README.md                 # Documentation
```

## Setup Instructions

### 1. Database

- Create a PostgreSQL database and user.
- Run the schema in `src/data/products.sql` to create the `products` table.
- To add Ceneo link support, run the migration in `src/data/add_ceneo_url.sql`.

### 2. Backend

- Install Python dependencies: `pip install -r requirements.txt`
- Configure your database credentials in `src/app.py` or `.env`.
- Run the backend:
	```bash
	python src/app.py
	```

### 3. Frontend

- Install Node.js dependencies:
	```bash
	npm install
	```
- Start the development server:
	```bash
	npm run dev
	```
- The app will be available at `http://localhost:5173` (frontend) and `http://localhost:5001` (backend API).

## Usage

- Visit the home page to browse products.
- Use the "Info/Kontakt" button for contact details.
- Admins can log in via `/admin`, add/edit/delete products, and set Ceneo links.
- If a product has a Ceneo link, the "Porównaj z Ceneo" button will appear on its card.

## Customization

- Edit styles in `src/styles/global.css`.
- Add or modify product categories in the admin form or backend.

## License

MIT
