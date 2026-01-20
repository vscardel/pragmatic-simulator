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

Firsy, transpile the TypeScript code to JavaScript:

```bash
cd dashboard
npm install
npx tsc
```

or to watch for changes run it in another terminal:

```bash
cd dashboard
npm install
npx tsc --watch
```

Then, run the FastAPI application:

```bash
fastapi dev main.py
```
