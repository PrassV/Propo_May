import React from 'react';
import { NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Home,
  Building2,
  Users,
  Wrench,
  CreditCard,
  Settings,
  LogOut
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Sidebar = () => {
  const { signOut } = useAuth();

  const navItems = [
    { icon: Home, label: 'Dashboard', path: '/dashboard' },
    { icon: Building2, label: 'Properties', path: '/properties' },
    { icon: Users, label: 'Tenants', path: '/tenants' },
    { icon: Wrench, label: 'Maintenance', path: '/maintenance' },
    { icon: CreditCard, label: 'Payments', path: '/payments' },
    { icon: Settings, label: 'Settings', path: '/settings' },
  ];

  return (
    <div className="w-64 h-screen bg-gray-900 text-white flex flex-col">
      <div className="p-4 border-b border-gray-800">
        <div className="flex items-center space-x-2">
          <Building2 className="w-8 h-8 text-blue-400" />
          <h1 className="text-xl font-bold">PropManage</h1>
        </div>
      </div>
      
      <nav className="flex-1 py-6 px-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => 
              `flex items-center space-x-3 px-3 py-2.5 rounded-md transition-colors ${
                isActive 
                  ? 'bg-blue-700 text-white' 
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
                {isActive && (
                  <motion.div
                    className="absolute left-0 w-1 h-8 bg-blue-400 rounded-r-full"
                    layoutId="activeNav"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.2 }}
                  />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>
      
      <div className="p-4 border-t border-gray-800">
        <button 
          onClick={signOut}
          className="flex items-center w-full space-x-3 px-3 py-2.5 text-gray-300 rounded-md hover:bg-gray-800 hover:text-white transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span>Sign Out</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;