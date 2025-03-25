# InboxArmour

InboxArmour is a real-time educational phishing email detection tool. It integrates with Gmail via OAuth authentication and uses Cohere's AI-powered language analysis to provide users with insights about potentially malicious emails.

## Features

- **Real-time Email Analysis**: Detects phishing attempts and provides immediate feedback.
- **Educational Warnings**: Explains why an email might be dangerous to help users recognize phishing attempts.
- **Gmail Integration**: Uses OAuth to securely analyze emails.
- **Cohere AI-powered Detection**: Leverages Cohere's NLP models for phishing analysis.
- **Flask Backend & React Frontend**: Modern web technology stack for a seamless user experience.

## Tech Stack

- **Backend**: Flask (Python) with OAuth authentication
- **Frontend**: React (TypeScript) with Vite and ESLint
- **Database**: SQLite/PostgreSQL (configurable)
- **AI Integration**: Cohere NLP API

## Getting Started

### Prerequisites

- Python 3.x
- Node.js & npm
- Gmail API credentials (OAuth 2.0 Client ID)

### Backend Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/IDontKnow64/InboxArmour.git
   cd InboxArmour/backend
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up environment variables (create a `.env` file and add required keys, including Gmail OAuth credentials).
5. Run the backend:
   ```sh
   flask run
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```sh
   cd ../frontend
   ```
2. Install dependencies:
   ```sh
   npm install
   ```
3. Start the React app:
   ```sh
   npm start
   ```

### Project Structure

To maintain a clean and organized codebase, you can structure your project as follows:

```
InboxArmour/
│── backend/             # Flask backend
│   ├── app.py           # Main application file
│   ├── models/          # Database models
│   ├── routes/          # API route definitions
│   ├── services/        # Business logic & integrations
│   ├── static/          # Static files (if needed)
│   ├── templates/       # HTML templates (if applicable)
│   ├── .env             # Environment variables
│
│── frontend/            # React frontend (TypeScript + Vite)
│   ├── src/             # Source files
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Page components
│   │   ├── hooks/       # Custom React hooks
│   │   ├── utils/       # Helper functions
│   │   ├── assets/      # Images, icons, etc.
│   ├── public/          # Static assets
│   ├── index.tsx        # Entry point
│   ├── vite.config.ts   # Vite configuration
│
│── README.md            # Project documentation
│── LICENSE              # License information
```

### Expanding ESLint Configuration

For better TypeScript linting, update `eslint.config.js`:

```js
export default tseslint.config({
  extends: [
    ...tseslint.configs.recommendedTypeChecked,
    ...tseslint.configs.strictTypeChecked,
    ...tseslint.configs.stylisticTypeChecked,
  ],
  languageOptions: {
    parserOptions: {
      project: ['./tsconfig.node.json', './tsconfig.app.json'],
      tsconfigRootDir: import.meta.dirname,
    },
  },
})
```

You can also install additional plugins for React-specific linting:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config({
  plugins: {
    'react-x': reactX,
    'react-dom': reactDom,
  },
  rules: {
    ...reactX.configs['recommended-typescript'].rules,
    ...reactDom.configs.recommended.rules,
  },
})
```

## Usage

Once both the frontend and backend are running, navigate to `http://localhost:5173/` in your browser. Log in with Gmail to authorize access, and InboxArmour will analyze your emails in real-time, flagging potential phishing attempts.

## Reference

This project is structured based on the best practices from the [Creating a Chrome Extension with React and Vite Boilerplate](https://medium.com/@5tigerjelly/creating-a-chrome-extension-with-react-and-vite-boilerplate-provided-db3d14473bf6) and modern React development standards using Vite and TypeScript.

## Future Plans

- **Localized and Specialized AI Model**: Develop a proprietary AI model tailored specifically for email security to improve detection accuracy.
- **Compare and Contrast AI Models**: Implement a system to compare multiple AI models in real-time, selecting the best-performing one for enhanced security.
- **Hidden Verification Exchange with Companies**: Collaborate with authentic companies to create a hidden verification mechanism, improving email trustworthiness without exposing sensitive data.

## Contributing

We welcome contributions! To contribute:
1. Fork the repository.
2. Create a new branch:
   ```sh
   git checkout -b feature/your-feature-name
   ```
3. Make your changes and commit:
   ```sh
   git commit -m "Description of changes"
   ```
4. Push to your fork:
   ```sh
   git push origin feature/your-feature-name
   ```
5. Open a pull request!

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

For any inquiries or issues, feel free to open an issue on GitHub or contact the maintainers directly.

