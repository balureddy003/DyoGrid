import React, { useEffect, useContext } from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Playground from './pages/Playground'
import Agents from './pages/Agents'
import PlaygroundHistory from './pages/Playground-history'
import Introduction from './pages/Introduction'
import GetStarted from './pages/GetStarted'
import GeneralSettings from './pages/GeneralSettings'
import './index.css'
import { UserProvider, UserContext, getUserInfo } from './contexts/UserContext'
import { TeamsProvider } from './contexts/TeamsContext'

function App() {
  const [isLoading, setIsLoading] = React.useState(true);
  const { setUserInfo } = useContext(UserContext);

  useEffect(() => {
    async function loadUser() {
      const user = await getUserInfo();
      setUserInfo(user);
      setIsLoading(false);
    }
    loadUser();
  }, []);

  if (isLoading) {
    return <div>Loading user info...</div>;
  }

  return (
    <Routes>
      <Route path="/" element={<Playground />} />
      <Route path="/agents" element={<Agents />} />
      <Route path="/playground-history" element={<PlaygroundHistory />} />
      <Route path="/introduction" element={<Introduction />} />
      <Route path="/get-started" element={<GetStarted />} />
      <Route path="/general" element={<GeneralSettings />} />
    </Routes>
  );
}

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <UserProvider>
      <TeamsProvider>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </TeamsProvider>
    </UserProvider>
  </React.StrictMode>
)