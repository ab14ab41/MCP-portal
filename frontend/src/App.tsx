import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import HomePage from './pages/HomePage';
import ProjectDetailPage from './pages/ProjectDetailPage';
import EndpointSelectionPage from './pages/EndpointSelectionPage';
import DeployedMCPsPage from './pages/DeployedMCPsPage';
import AITestingPage from './pages/AITestingPage';
import DocumentationPage from './pages/DocumentationPage';

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
          <Route path="/specs/:specId/endpoints" element={<EndpointSelectionPage />} />
          <Route path="/deployed-mcps" element={<DeployedMCPsPage />} />
          <Route path="/ai-testing" element={<AITestingPage />} />
          <Route path="/documentation" element={<DocumentationPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
