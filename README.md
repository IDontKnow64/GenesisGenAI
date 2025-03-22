# GenesisGenAI

Resources:
React + Vite Chrome extension:
https://medium.com/@5tigerjelly/creating-a-chrome-extension-with-react-and-vite-boilerplate-provided-db3d14473bf6

### Install backend
```
cd backend
pip install -r requirements.txt
```


### Starting backend
```
cd backend
venv\Scripts\Activate   # Windows (PowerShell in VS Code)
# OR
source venv/bin/activate   # macOS/Linux
flask run
```

### Install Frontend
```
cd frontend
npm install
```

### Start React Frontend
```
cd frontend
npm run dev
```

### Build
```
cd frontend
npm run build
```
Then go to `chrome://extensions/` enable ‘Developer mode’ and ‘Load unpacked’ by selecting the build directory that was just created!


### Load Chrome Extension
Open Google Chrome
Go to chrome://extensions/
Enable Developer Mode
Click "Load Unpacked" and select the extensions/ folder


### File structure
```
email-scam-detector/
│── backend/               # Flask Backend
│   ├── venv/              # Virtual environment
│   ├── app/               # Main application folder
│   │   ├── __init__.py
│   │   ├── routes.py      # API routes
│   │   ├── model.py       # ML Model logic (if needed)
│   │   ├── utils.py       # Helper functions
│   ├── static/            # Any static files Flask serves
│   ├── templates/         # HTML templates (if needed)
│   ├── requirements.txt   # Python dependencies
│   ├── config.py          # Configuration settings
│   ├── run.py             # Flask entry point
│── frontend/              # React Frontend
│   ├── node_modules/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── utils/
│   │   ├── App.tsx
│   │   ├── index.tsx
│   ├── package.json
│   ├── vite.config.ts     # Vite configuration
│── extensions/            # Chrome Extension Logic
│   ├── manifest.json      # Chrome extension manifest
│   ├── background.js      # Background script
│   ├── content.js         # Content script
│   ├── popup/             # Popup UI (React)
│   │   ├── index.html
│   │   ├── popup.tsx
│   ├── styles.css
│── .gitignore
│── README.md
│── package.json           # Root package.json (for tooling)
│── pyproject.toml         # Backend dependency management (optional)
│── docker-compose.yml     # Docker setup (optional)
│── .env                   # Environment variables
```