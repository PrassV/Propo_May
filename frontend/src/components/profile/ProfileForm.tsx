import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Phone, Mail, Building2, Home } from 'lucide-react';
import Input from '../ui/Input';
import Button from '../ui/Button';
import Select from '../ui/Select';
import { useAuth } from '../../context/AuthContext';

const ProfileForm = () => {
  const navigate = useNavigate();
  const { user, updateUserProfile } = useAuth();
  
  const [formData, setFormData] = useState({
    firstName: user?.firstName || '',
    lastName: user?.lastName || '',
    email: user?.email || '',
    phone: user?.phone || '',
    role: user?.role || '',
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      await updateUserProfile({
        firstName: formData.firstName,
        lastName: formData.lastName,
        phone: formData.phone,
        role: formData.role as 'owner' | 'tenant' | null,
      });
      
      navigate('/dashboard');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update profile';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="max-w-2xl mx-auto p-8 bg-white rounded-lg shadow-md">
      <div className="flex items-center space-x-3 mb-6">
        <div className="bg-blue-100 p-2 rounded-full">
          <User className="h-6 w-6 text-blue-700" />
        </div>
        <h2 className="text-2xl font-bold text-gray-800">Complete Your Profile</h2>
      </div>
      
      <p className="text-gray-600 mb-8">
        Please fill in your information to continue. This will help us personalize your experience.
      </p>
      
      {error && (
        <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-md">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div>
            <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-1">
              First Name
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <User className="h-5 w-5 text-gray-400" />
              </div>
              <Input
                id="firstName"
                name="firstName"
                type="text"
                value={formData.firstName}
                onChange={handleChange}
                className="pl-10"
                placeholder="Enter your first name"
                required
              />
            </div>
          </div>
          
          <div>
            <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 mb-1">
              Last Name
            </label>
            <Input
              id="lastName"
              name="lastName"
              type="text"
              value={formData.lastName}
              onChange={handleChange}
              placeholder="Enter your last name"
              required
            />
          </div>
        </div>
        
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
            Email
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Mail className="h-5 w-5 text-gray-400" />
            </div>
            <Input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              disabled
              className="pl-10 bg-gray-50"
            />
          </div>
          <p className="mt-1 text-xs text-gray-500">Your email cannot be changed</p>
        </div>
        
        <div>
          <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
            Phone Number
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Phone className="h-5 w-5 text-gray-400" />
            </div>
            <Input
              id="phone"
              name="phone"
              type="tel"
              value={formData.phone}
              onChange={handleChange}
              className="pl-10"
              placeholder="Enter your phone number"
              required
            />
          </div>
        </div>
        
        <div>
          <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-1">
            I am a...
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              {formData.role === 'owner' ? (
                <Building2 className="h-5 w-5 text-gray-400" />
              ) : (
                <Home className="h-5 w-5 text-gray-400" />
              )}
            </div>
            <Select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleChange}
              className="pl-10"
              options={[
                { label: 'Select your role', value: '' },
                { label: 'Property Owner', value: 'owner' },
                { label: 'Tenant', value: 'tenant' },
              ]}
              required
            />
          </div>
        </div>
        
        <div className="pt-4">
          <Button type="submit" className="w-full py-2.5" disabled={isLoading}>
            {isLoading ? 'Saving...' : 'Complete Profile'}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default ProfileForm;