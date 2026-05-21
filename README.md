# How to install?

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment:

- On Windows: `venv\Scripts\activate`
- On Unix: `source venv/bin/activate`

Install the required packages:

```bash
pip install -r requirements.txt
```

# How to run?

Firsy, run the FastApi application:

```bash
fastapi dev main.py
```

open another terminal in root folder of project and run the frontend:

```bash
cd frontend
npm install
npm run build
npm run start
```

Or, in dev mode:

```bash
cd frontend
npm install
npm run dev
```
