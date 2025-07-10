## 🚀 Getting Started

### 🔧 Requirements

* Python 3.11+ (recommended: via [pyenv](https://github.com/pyenv/pyenv))
* Docker & Docker Compose
* Poetry (for Python dependency management)

---

### 🛠️ Installation & Setup

1. **Clone the repo**

   ```bash
   git clone https://github.com/Axmouth/movierama.git
   cd movierama
   ```

2. **Start the local dev environment**

   ```bash
   docker-compose up --build
   ```

   This will start:

   * Django app ([http://localhost:8000](http://localhost:8000))
   * Postgres DB (on internal Docker network)

3. **Apply migrations & create a superuser**

   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

4. **(Optional) Load sample data**

   ```bash
   docker-compose exec web python manage.py loaddata sample_data.json
   ```

---

### ✅ Running Tests

```bash
docker-compose exec web pytest
```

You can also check coverage:

```bash
docker-compose exec web pytest --cov
```

---

## 🚀 Running Locally with Poetry

> Useful if you prefer not to use Docker.

### ✅ Prerequisites

* Python 3.11+
* [Poetry](https://python-poetry.org/docs/#installation)
* PostgreSQL (or edit `DATABASE_URL` to use SQLite)

### ⚙️ Setup Steps

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Axmouth/movierama.git
   cd movierama
   ```

2. **Install dependencies**:

   ```bash
   poetry install
   ```

3. **Set up environment variables** (if needed):

   ```bash
   export DATABASE_URL=postgres://devuser:devpass@localhost:5433/movierama
   export DJANGO_DEBUG=True
   ```

4. **Run migrations**:

   ```bash
   poetry run python manage.py migrate
   ```

5. **Create a superuser** (optional):

   ```bash
   poetry run python manage.py createsuperuser
   ```

6. **Run the development server**:

   ```bash
   poetry run python manage.py runserver 0.0.0.0:8000
   ```

Then visit [http://localhost:8000](http://localhost:8000)

---

## 📝 What’s Implemented

* User signup/login/logout
* Submit movies (linked to creator)
* Like / Hate voting system (toggleable)
* No voting on own movies
* Sorting by likes/hates/date
* View all movies by user
* Auth-required views
* Flash messages & vote feedback
* Pagination
* Full test suite with coverage
