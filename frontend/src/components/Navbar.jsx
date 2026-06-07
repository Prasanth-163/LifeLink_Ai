import React, { useEffect, useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Droplet, LogOut, User, LayoutDashboard } from 'lucide-react';

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [role, setRole] = useState(localStorage.getItem('role'));

  useEffect(() => {
    setToken(localStorage.getItem('token'));
    setRole(localStorage.getItem('role'));
  }, [location]);

  const handleLogout = () => {
    localStorage.clear();
    setToken(null);
    setRole(null);
    navigate('/login');
  };

  return (
    <nav className="p-4 bg-white shadow-md flex justify-between items-center px-6 md:px-10 sticky top-0 z-50">
      <Link to={token ? `/${role}-dashboard` : "/"} className="text-2xl font-bold text-primary flex items-center gap-2">
        <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-white shadow-lg shadow-red-200">
          <Droplet size={24} fill="currentColor" />
        </div>
        <span className="hidden md:block tracking-tight">LifeLink AI</span>
      </Link>
      
      <div className="flex items-center gap-4 md:gap-8 font-semibold">
        {!token ? (
          <>
            <Link to="/" className="text-gray-600 hover:text-primary transition hidden md:block">Home</Link>
            <Link to="/login" className="text-gray-600 hover:text-primary transition">Login</Link>
            <Link to="/register" className="px-6 py-2 bg-primary text-white rounded-xl hover:bg-secondary transition shadow-md shadow-red-100">Register</Link>
          </>
        ) : (
          <>
            <Link to={`/${role}-dashboard`} className="flex items-center gap-1.5 text-gray-600 hover:text-primary transition">
              <LayoutDashboard size={18} /> <span className="hidden md:inline">Dashboard</span>
            </Link>
            <Link to="/profile" className="flex items-center gap-1.5 text-gray-600 hover:text-primary transition">
              <User size={18} /> <span className="hidden md:inline">Profile</span>
            </Link>
            <button 
              onClick={handleLogout}
              className="flex items-center gap-1.5 text-red-400 hover:text-red-600 transition"
            >
              <LogOut size={18} /> <span className="hidden md:inline">Logout</span>
            </button>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;

