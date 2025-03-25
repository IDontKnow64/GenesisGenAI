// src/App.tsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/Home/Home.tsx'
import MailPage from './pages/Mail/Mail.tsx'
import LoginPage from './pages/Login/Login.tsx'

// Define route configuration type
type RouteConfig = {
  path: string;
  component: React.ComponentType;
};

const routes: RouteConfig[] = [
  { path: '/', component: HomePage },
  { path: '/login', component: LoginPage },
  { path: '/mail', component: MailPage },
  // { path: '*', component: NotFound }
];

const App = () => {
  return (
    <Router>
      <Routes>
        {routes.map(({ path, component: Component }) => (
          <Route key={path} path={path} element={<Component />} />
        ))}
      </Routes>
    </Router>
  );
};

export default App;