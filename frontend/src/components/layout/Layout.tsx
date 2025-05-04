import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

const Layout = () => {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 overflow-x-hidden overflow-y-auto">
        <Outlet />
      </div>
    </div>
  );
};

export default Layout;