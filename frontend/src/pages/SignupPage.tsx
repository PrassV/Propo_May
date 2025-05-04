import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import SignupForm from '../components/auth/SignupForm';

const SignupPage = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <Link to="/" className="flex items-center text-sm text-gray-600 hover:text-gray-900 mb-6 ml-8">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back to home
        </Link>
        <SignupForm />
      </div>
    </div>
  );
};

export default SignupPage;