import React from 'react';
import { Building2 } from 'lucide-react';
import ProfileForm from '../components/profile/ProfileForm';

const ProfilePage = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center p-3 bg-blue-100 rounded-full">
            <Building2 className="h-8 w-8 text-blue-700" />
          </div>
          <h1 className="mt-4 text-3xl font-bold text-gray-900">Welcome to PropManage</h1>
          <p className="mt-2 text-lg text-gray-600">
            Let's get started by setting up your profile
          </p>
        </div>
        
        <ProfileForm />
      </div>
    </div>
  );
};

export default ProfilePage;