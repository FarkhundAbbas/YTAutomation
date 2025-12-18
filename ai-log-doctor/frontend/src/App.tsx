import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Activity, AlertTriangle, FileText, Settings, LogOut, Home, Menu, X } from 'lucide-react';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ErrorExplorer from './pages/ErrorExplorer';
import Proposals from './pages/Proposals';
import SettingsPage from './pages/Settings';
import './index.css';

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('token'));

    const handleLogout = () => {
        localStorage.removeItem('token');
        setIsAuthenticated(false);
    };

    if (!isAuthenticated) {
        return <Login onLoginSuccess={() => setIsAuthenticated(true)} />;
    }

    return (
        <BrowserRouter>
            <AppLayout onLogout={handleLogout} />
        </BrowserRouter>
    );
}

interface AppLayoutProps {
    onLogout: () => void;
}

const AppLayout: React.FC<AppLayoutProps> = ({ onLogout }) => {
    const [sidebarOpen, setSidebarOpen] = useState(true);

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            {/* Sidebar */}
            <div className={`fixed left-0 top-0 h-full ${sidebarOpen ? 'w-72' : 'w-20'} bg-slate-800/95 backdrop-blur-sm border-r border-slate-700/50 flex flex-col transition-all duration-300 shadow-2xl z-50`}>
                {/* Header */}
                <div className="p-6 border-b border-slate-700/50">
                    <div className="flex items-center justify-between">
                        {sidebarOpen ? (
                            <>
                                <div>
                                    <h1 className="text-xl font-bold text-white flex items-center space-x-2">
                                        <div className="p-2 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg shadow-lg">
                                            <Activity className="w-5 h-5 text-white" />
                                        </div>
                                        <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                                            AI Log Doctor
                                        </span>
                                    </h1>
                                    <p className="text-xs text-gray-400 mt-2 ml-11">Self-Healing Intelligence</p>
                                </div>
                                <button
                                    onClick={() => setSidebarOpen(false)}
                                    className="p-2 hover:bg-slate-700/50 rounded-lg transition-colors"
                                >
                                    <X className="w-5 h-5 text-gray-400" />
                                </button>
                            </>
                        ) : (
                            <button
                                onClick={() => setSidebarOpen(true)}
                                className="p-2 hover:bg-slate-700/50 rounded-lg transition-colors mx-auto"
                            >
                                <Menu className="w-6 h-6 text-gray-400" />
                            </button>
                        )}
                    </div>
                </div>

                {/* Navigation */}
                <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
                    <NavLink to="/" icon={<Home className="w-5 h-5" />} text="Dashboard" collapsed={!sidebarOpen} />
                    <NavLink to="/errors" icon={<AlertTriangle className="w-5 h-5" />} text="Error Explorer" collapsed={!sidebarOpen} />
                    <NavLink to="/proposals" icon={<FileText className="w-5 h-5" />} text="Proposals" collapsed={!sidebarOpen} />
                    <NavLink to="/validation" icon={<Settings className="w-5 h-5" />} text="SIEM Integrations" collapsed={!sidebarOpen} />
                </nav>

                {/* User Section */}
                <div className="p-4 border-t border-slate-700/50">
                    <button
                        onClick={onLogout}
                        className={`w-full flex items-center ${sidebarOpen ? 'space-x-3 px-4' : 'justify-center'} py-3 text-gray-300 hover:bg-red-500/10 hover:text-red-400 rounded-lg transition-all group`}
                        title={!sidebarOpen ? "Logout" : ""}
                    >
                        <LogOut className="w-5 h-5 group-hover:scale-110 transition-transform" />
                        {sidebarOpen && <span className="font-medium">Logout</span>}
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className={`${sidebarOpen ? 'ml-72' : 'ml-20'} p-8 transition-all duration-300`}>
                <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/errors" element={<ErrorExplorer />} />
                    <Route path="/proposals" element={<Proposals />} />
                    <Route path="/validation" element={<SettingsPage />} />
                </Routes>
            </div>
        </div>
    );
};

interface NavLinkProps {
    to: string;
    icon: React.ReactNode;
    text: string;
    collapsed: boolean;
}

const NavLink: React.FC<NavLinkProps> = ({ to, icon, text, collapsed }) => {
    const location = useLocation();
    const isActive = location.pathname === to;

    return (
        <Link
            to={to}
            className={`flex items-center ${collapsed ? 'justify-center' : 'space-x-3 px-4'} py-3 rounded-lg transition-all group relative ${isActive
                ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-white border border-cyan-500/30 shadow-lg shadow-cyan-500/10'
                : 'text-gray-400 hover:bg-slate-700/50 hover:text-white'
                }`}
            title={collapsed ? text : ""}
        >
            <div className={`${isActive ? 'text-cyan-400' : 'group-hover:text-cyan-400'} transition-colors`}>
                {icon}
            </div>
            {!collapsed && <span className="font-medium">{text}</span>}
            {isActive && !collapsed && (
                <div className="absolute right-2 w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse"></div>
            )}
        </Link>
    );
};

export default App;
