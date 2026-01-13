import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import RegisterFace from './pages/RegisterFace';
import RegisterMultipleFaces from './pages/RegisterMultipleFaces';
import MatchFace from './pages/MatchFace';
import LiveAttendance from './pages/LiveAttendance';
import EmployeeDashboard from './pages/EmployeeDashboard';
import { ThemeProvider } from "@/components/theme-provider"
import './App.css'
import Dashboard from './pages/dashboard';

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/register-face" element={<RegisterFace />} />
            <Route path="/match-face" element={<MatchFace/>} />
            <Route path="/live-attendance" element={<LiveAttendance />} />
            <Route path="/employee-dashboard" element={<EmployeeDashboard />} />
            <Route path="/register-multiple-faces" element={<RegisterMultipleFaces />} />
            <Route path="/" element={<Navigate to="/login" />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
