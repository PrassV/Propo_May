import React from 'react';
import { Settings, User, Building2, CreditCard, Bell, Shield, LogOut } from 'lucide-react';
import Header from '../components/layout/Header';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import { useAuth } from '../context/AuthContext';

const SettingsPage = () => {
  const { user, signOut } = useAuth();
  
  return (
    <div className="min-h-screen">
      <Header title="Settings" />
      
      <main className="p-6">
        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-12 md:col-span-3">
            <Card>
              <CardContent className="p-0">
                <nav className="flex flex-col">
                  {[
                    { icon: User, label: 'Profile', active: true },
                    { icon: Building2, label: 'Company' },
                    { icon: CreditCard, label: 'Billing' },
                    { icon: Bell, label: 'Notifications' },
                    { icon: Shield, label: 'Security' },
                  ].map((item, index) => (
                    <button
                      key={index}
                      className={`flex items-center px-4 py-3 text-sm ${
                        item.active 
                          ? 'bg-blue-50 text-blue-700 font-medium border-l-2 border-blue-700' 
                          : 'text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      <item.icon className="h-5 w-5 mr-2" />
                      {item.label}
                    </button>
                  ))}
                  
                  <button
                    onClick={signOut}
                    className="flex items-center px-4 py-3 text-sm text-red-600 hover:bg-red-50 mt-auto"
                  >
                    <LogOut className="h-5 w-5 mr-2" />
                    Sign Out
                  </button>
                </nav>
              </CardContent>
            </Card>
          </div>
          
          <div className="col-span-12 md:col-span-9">
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">Profile Settings</CardTitle>
              </CardHeader>
              <CardContent>
                <form className="space-y-6">
                  <div className="flex flex-col sm:flex-row gap-6">
                    <div className="flex-1">
                      <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-1">
                        First Name
                      </label>
                      <Input 
                        id="firstName" 
                        defaultValue={user?.firstName} 
                      />
                    </div>
                    <div className="flex-1">
                      <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 mb-1">
                        Last Name
                      </label>
                      <Input 
                        id="lastName" 
                        defaultValue={user?.lastName} 
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                      Email
                    </label>
                    <Input 
                      id="email" 
                      type="email" 
                      defaultValue={user?.email} 
                      disabled
                      className="bg-gray-50" 
                    />
                    <p className="mt-1 text-xs text-gray-500">Your email cannot be changed</p>
                  </div>
                  
                  <div>
                    <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
                      Phone Number
                    </label>
                    <Input 
                      id="phone" 
                      type="tel" 
                      defaultValue={user?.phone} 
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Profile Image
                    </label>
                    <div className="flex items-center">
                      <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 mr-4">
                        <User className="h-8 w-8" />
                      </div>
                      <div>
                        <Button variant="outline" size="sm" className="mb-1">
                          Upload Image
                        </Button>
                        <p className="text-xs text-gray-500">
                          JPG, GIF or PNG. 1MB max.
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="pt-4 border-t border-gray-200">
                    <Button>Save Changes</Button>
                  </div>
                </form>
              </CardContent>
            </Card>
            
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="text-xl">Password</CardTitle>
              </CardHeader>
              <CardContent>
                <form className="space-y-6">
                  <div>
                    <label htmlFor="currentPassword" className="block text-sm font-medium text-gray-700 mb-1">
                      Current Password
                    </label>
                    <Input 
                      id="currentPassword" 
                      type="password" 
                    />
                  </div>
                  
                  <div className="flex flex-col sm:flex-row gap-6">
                    <div className="flex-1">
                      <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700 mb-1">
                        New Password
                      </label>
                      <Input 
                        id="newPassword" 
                        type="password" 
                      />
                    </div>
                    <div className="flex-1">
                      <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                        Confirm New Password
                      </label>
                      <Input 
                        id="confirmPassword" 
                        type="password" 
                      />
                    </div>
                  </div>
                  
                  <div className="pt-4">
                    <Button>Update Password</Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
};

export default SettingsPage;