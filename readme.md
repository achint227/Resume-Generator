# Resume Build Backend

This project is based on [Resume-Generator](https://github.com/cczhong11/Resume-Generator). It generates tailored resumes for different companies and job roles using LaTeX templates.

The resume data is stored in a database (SQLite or MongoDB) and can be edited using [resume-ui](https://github.com/achint227/resume/tree/main/).

## Project Structure

```
.
├── app.py                  # Main Flask application entry point
├── src/
│   ├── api/               # API routes and endpoints
│   │   └── routes.py
│   ├── database/          # Database operations
│   │   └── operations.py
│   ├── templates/         # Resume template classes
│   │   ├── base.py       # Base template class
│   │   ├── moderncv.py   # ModernCV template
│   │   ├── template1.py  # Resume template
│   │   └── template2.py  # Russell template
│   └── config.py         # Configuration
├── assets/               # Generated PDF output
├── moderncv/            # ModernCV LaTeX files
├── resume/              # Resume LaTeX files
├── russel/              # Russell LaTeX files
└── requirements.txt     # Python dependencies
```

## Install

Make sure you have the following software:

- texlive (for LaTeX compilation)
- Python 3.8+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package manager)

### Setup with UV

Install dependencies using UV:

```bash
uv sync
```

This will create a virtual environment and install all dependencies from `pyproject.toml`.

## Configuration

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

### Database Options

The project auto-detects which database to use:

**SQLite (default):**
- No configuration needed
- Database file created automatically at `resumes.db`
- Perfect for local development

**MongoDB:**
Add `DATABASE_URL` to your `.env`:
```env
DATABASE_URL=mongodb://your-connection-string
```

Install the MongoDB dependency:
```bash
uv sync --extra mongodb
```

## Run

Start the Flask server using UV:

```bash
uv run python app.py
```

Or activate the virtual environment and run directly:

```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python app.py
```

The server will run on `http://0.0.0.0:8000`

## API Endpoints

- `GET /` - Health check
- `GET /resume` - Get all resumes
- `GET /resume/<name>` - Get resume by name
- `GET /resume/user/<name>` - Get resume by user name
- `POST /resume` - Add new resume
- `GET /download/<id>/<template>/<order>` - Download resume PDF
- `GET /copy/<id>/<template>/<order>` - Get resume LaTeX source

### Templates

- `moderncv` - Modern CV template
- `resume` - Classic resume template
- `russel` - Russell template

### Order Parameter

The `order` parameter controls section ordering (3 characters):
- `p` - Projects
- `w` - Work Experience
- `e` - Education

Example: `pwe` = Projects, Work Experience, Education
