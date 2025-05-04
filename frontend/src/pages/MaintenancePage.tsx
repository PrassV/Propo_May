import React, { useState } from 'react';
import { Wrench, Plus, Search, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import Header from '../components/layout/Header';
import { Card, CardContent } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Select from '../components/ui/Select';
import { useApp } from '../context/AppContext';
import { formatDate } from '../lib/utils';

const MaintenancePage = () => {
  const { maintenanceRequests, properties, isLoading } = useApp();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  
  const filteredRequests = maintenanceRequests.filter((request) => {
    const matchesSearch = 
      request.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      request.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      request.unitNumber.toLowerCase().includes(searchQuery.toLowerCase());
      
    const matchesStatus = statusFilter === 'all' || request.status === statusFilter;
    const matchesPriority = priorityFilter === 'all' || request.priority === priorityFilter;
    
    return matchesSearch && matchesStatus && matchesPriority;
  });
  
  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'low':
        return <Clock className="h-5 w-5 text-green-500" />;
      case 'medium':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'high':
        return <AlertCircle className="h-5 w-5 text-orange-500" />;
      case 'emergency':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'new':
        return <AlertCircle className="h-5 w-5 text-blue-500" />;
      case 'in_progress':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'cancelled':
        return <AlertCircle className="h-5 w-5 text-gray-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-500" />;
    }
  };
  
  return (
    <div className="min-h-screen">
      <Header title="Maintenance Requests" />
      
      <main className="p-6">
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-6 gap-4">
          <div className="flex flex-col sm:flex-row gap-4 w-full lg:w-auto">
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <Input
                type="text"
                placeholder="Search requests..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              options={[
                { label: 'All Status', value: 'all' },
                { label: 'New', value: 'new' },
                { label: 'In Progress', value: 'in_progress' },
                { label: 'Completed', value: 'completed' },
                { label: 'Cancelled', value: 'cancelled' },
              ]}
              className="w-full sm:w-40"
            />
            
            <Select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              options={[
                { label: 'All Priority', value: 'all' },
                { label: 'Low', value: 'low' },
                { label: 'Medium', value: 'medium' },
                { label: 'High', value: 'high' },
                { label: 'Emergency', value: 'emergency' },
              ]}
              className="w-full sm:w-40"
            />
          </div>
          
          <Button className="flex items-center whitespace-nowrap">
            <Plus className="h-5 w-5 mr-1" />
            New Request
          </Button>
        </div>
        
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Request
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Property / Unit
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Priority
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredRequests.map((request) => {
                  const property = properties.find(p => p.id === request.propertyId);
                  
                  return (
                    <tr key={request.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{request.title}</div>
                        <div className="text-sm text-gray-500 truncate max-w-xs">{request.description}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{property?.name}</div>
                        <div className="text-sm text-gray-500">Unit {request.unitNumber}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {getPriorityIcon(request.priority)}
                          <span className={`ml-1.5 text-sm font-medium capitalize ${
                            request.priority === 'low' ? 'text-green-800' :
                            request.priority === 'medium' ? 'text-yellow-800' :
                            request.priority === 'high' ? 'text-orange-800' :
                            'text-red-800'
                          }`}>
                            {request.priority}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {getStatusIcon(request.status)}
                          <span className="ml-1.5 text-sm font-medium capitalize">
                            {request.status.replace('_', ' ')}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(request.createdAt)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <Button variant="ghost" size="sm">View</Button>
                        <Button variant="ghost" size="sm" className="text-blue-600">Update</Button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            
            {filteredRequests.length === 0 && (
              <div className="flex flex-col items-center justify-center py-12">
                <div className="bg-gray-100 p-3 rounded-full mb-3">
                  <Wrench className="h-6 w-6 text-gray-500" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-1">No maintenance requests found</h3>
                <p className="text-gray-500 text-center mb-4">
                  {searchQuery || statusFilter !== 'all' || priorityFilter !== 'all'
                    ? 'Try adjusting your filters'
                    : 'Create your first maintenance request to get started'}
                </p>
                <Button>
                  <Plus className="h-5 w-5 mr-1" />
                  New Request
                </Button>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default MaintenancePage;