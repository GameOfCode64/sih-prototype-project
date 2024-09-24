import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/sidebar.tsx";
import NetworkLogs from "./components/NetworkLogs.tsx";
import Alerts from "./components/Alerts.tsx";
import GocAi from "./components/GocAi.tsx";

function App() {
  return (
    <BrowserRouter>
      <div className="flex flex-row space-x-5">
        <Sidebar />
        <Routes>
          <Route path="/" element={<NetworkLogs />} />
          <Route path="/security-alerts" element={<Alerts />} />
          <Route path="/goc-ai" element={<GocAi />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
