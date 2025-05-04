import React from 'react';
import { Bell, User } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

type HeaderProps = {
  title: string;
};

const Header = ({ title }: HeaderProps) => {
  const { user } = useAuth();
  
  return (
    <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-6">
      <h1 className="text-2xl font-bold text-gray-800">{title}</h1>
      
      <div className="flex items-center space-x-4">
        <button className="relative p-2 rounded-full hover:bg-gray-100 transition-colors">
          <Bell className="w-5 h-5 text-gray-600" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>
        
        <div className="flex items-center space-x-3">
          <div className="text-right">
            <p className="text-sm font-medium text-gray-700">
              {user?.firstName ? `${user.firstName} ${user.lastName}` : user?.email}
            </p>
            <p className="text-xs text-gray-500">{user?.role || 'Not set'}</p>
          </div>
          <div className="w-9 h-9 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
            {user?.avatarUrl ? (
              <img
                src={user.avatarUrl}
                alt="User avatar"
                className="w-full h-full rounded-full object-cover"
              />
            ) : (
              <User className="w-5 h-5" />
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;