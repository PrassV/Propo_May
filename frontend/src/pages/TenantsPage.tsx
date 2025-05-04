import React from 'react';
import { Users, Plus, Search, Calendar, Phone, Mail, ExternalLink } from 'lucide-react';
import Header from '../components/layout/Header';
import { Card, CardContent } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import { useApp } from '../context/AppContext';
import { formatCurrency, formatDate, daysRemaining } from '../lib/utils';

const TenantsPage = () => {
  const { tenants, properties, isLoading } = useApp();
  const [searchQuery, setSearchQuery] = React.useState('');
  
  const filteredTenants = tenants.filter(
    (tenant) => 
      tenant.userId.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tenant.unitNumber.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  return (
    <div className="min-h-screen">
      <Header title="Tenants" />
      
      <main className="p-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
          <div className="relative flex-1 max-w-md">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <Input
              type="text"
              placeholder="Search tenants..."
              className="pl-10"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          
          <Button className="flex items-center">
            <Plus className="h-5 w-5 mr-1" />
            Add Tenant
          </Button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTenants.map((tenant) => {
            const property = properties.find(p => p.id === tenant.propertyId);
            const daysLeft = daysRemaining(tenant.leaseEnd);
            
            return (
              <Card key={tenant.id} className="overflow-hidden hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 mr-3">
                        <Users className="h-5 w-5" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold">Tenant {tenant.id.split('-')[1]}</h3>
                        <p className="text-sm text-gray-500">Unit {tenant.unitNumber}</p>
                      </div>
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      tenant.status === 'active' 
                        ? 'bg-green-100 text-green-800' 
                        : tenant.status === 'pending'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-gray-100 text-gray-800'
                    }`}>
                      {tenant.status}
                    </span>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-sm text-gray-600">
                      {property?.name} - {property?.address}, {property?.city}
                    </p>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-3 mb-4">
                    <div className="flex items-center text-sm text-gray-600">
                      <Calendar className="h-4 w-4 mr-1 text-gray-400" />
                      <div>
                        <p className="text-xs text-gray-500">Lease Period</p>
                        <p>{formatDate(tenant.leaseStart)} - {formatDate(tenant.leaseEnd)}</p>
                      </div>
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <div>
                        <p className="text-xs text-gray-500">Monthly Rent</p>
                        <p className="font-medium">{formatCurrency(tenant.rentAmount)}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div 
                        className={`h-2.5 rounded-full ${
                          daysLeft > 90 ? 'bg-green-600' : 
                          daysLeft > 30 ? 'bg-yellow-500' : 'bg-red-600'
                        }`}
                        style={{ width: `${Math.min(100, Math.max(0, (daysLeft / 365) * 100))}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {daysLeft > 0 
                        ? `${daysLeft} days remaining on lease` 
                        : 'Lease expired'}
                    </p>
                  </div>
                  
                  <Button variant="outline" className="w-full flex items-center justify-center">
                    View Details
                    <ExternalLink className="h-4 w-4 ml-1" />
                  </Button>
                </CardContent>
              </Card>
            );
          })}
          
          {filteredTenants.length === 0 && (
            <div className="col-span-full flex flex-col items-center justify-center p-10 bg-gray-50 rounded-lg">
              <div className="bg-gray-100 p-3 rounded-full mb-3">
                <Users className="h-6 w-6 text-gray-500" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-1">No tenants found</h3>
              <p className="text-gray-500 text-center mb-4">
                {searchQuery ? 'Try adjusting your search' : 'Add your first tenant to get started'}
              </p>
              <Button>
                <Plus className="h-5 w-5 mr-1" />
                Add Tenant
              </Button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default TenantsPage;