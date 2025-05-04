import React, { useState } from 'react';
import { CreditCard, Plus, Search, ArrowUpCircle, ArrowDownCircle, Filter } from 'lucide-react';
import Header from '../components/layout/Header';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Select from '../components/ui/Select';
import { useApp } from '../context/AppContext';
import { formatCurrency, formatDate } from '../lib/utils';

const PaymentsPage = () => {
  const { payments, tenants, properties, isLoading } = useApp();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  
  const filteredPayments = payments.filter((payment) => {
    const matchesSearch = 
      payment.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      payment.tenantId.toLowerCase().includes(searchQuery.toLowerCase());
      
    const matchesStatus = statusFilter === 'all' || payment.status === statusFilter;
    const matchesType = typeFilter === 'all' || payment.type === typeFilter;
    
    return matchesSearch && matchesStatus && matchesType;
  });
  
  // Calculate total values
  const totalReceived = filteredPayments
    .filter(p => p.status === 'paid')
    .reduce((sum, payment) => sum + payment.amount, 0);
    
  const totalPending = filteredPayments
    .filter(p => p.status === 'pending')
    .reduce((sum, payment) => sum + payment.amount, 0);
    
  const totalOverdue = filteredPayments
    .filter(p => p.status === 'overdue')
    .reduce((sum, payment) => sum + payment.amount, 0);
  
  return (
    <div className="min-h-screen">
      <Header title="Payments" />
      
      <main className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Payments Received</p>
                <p className="text-2xl font-semibold text-gray-900">{formatCurrency(totalReceived)}</p>
              </div>
              <div className="p-3 rounded-full bg-green-100">
                <ArrowUpCircle className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Pending Payments</p>
                <p className="text-2xl font-semibold text-gray-900">{formatCurrency(totalPending)}</p>
              </div>
              <div className="p-3 rounded-full bg-yellow-100">
                <CreditCard className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Overdue Payments</p>
                <p className="text-2xl font-semibold text-gray-900">{formatCurrency(totalOverdue)}</p>
              </div>
              <div className="p-3 rounded-full bg-red-100">
                <ArrowDownCircle className="h-6 w-6 text-red-600" />
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-6 gap-4">
          <div className="flex flex-col sm:flex-row gap-4 w-full lg:w-auto">
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <Input
                type="text"
                placeholder="Search payments..."
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
                { label: 'Paid', value: 'paid' },
                { label: 'Pending', value: 'pending' },
                { label: 'Overdue', value: 'overdue' },
              ]}
              className="w-full sm:w-40"
            />
            
            <Select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              options={[
                { label: 'All Types', value: 'all' },
                { label: 'Rent', value: 'rent' },
                { label: 'Deposit', value: 'deposit' },
                { label: 'Fee', value: 'fee' },
                { label: 'Other', value: 'other' },
              ]}
              className="w-full sm:w-40"
            />
          </div>
          
          <Button className="flex items-center whitespace-nowrap">
            <Plus className="h-5 w-5 mr-1" />
            Record Payment
          </Button>
        </div>
        
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Payment ID
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tenant / Property
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Due Date
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredPayments.map((payment) => {
                  const property = properties.find(p => p.id === payment.propertyId);
                  const tenant = tenants.find(t => t.id === payment.tenantId);
                  
                  return (
                    <tr key={payment.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{payment.id}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">Tenant {payment.tenantId.split('-')[1]}</div>
                        <div className="text-sm text-gray-500">{property?.name} - Unit {tenant?.unitNumber}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800 capitalize">
                          {payment.type}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {formatCurrency(payment.amount)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(payment.dueDate)}
                        {payment.paidDate && (
                          <div className="text-xs text-gray-400">Paid: {formatDate(payment.paidDate)}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          payment.status === 'paid' 
                            ? 'bg-green-100 text-green-800' 
                            : payment.status === 'pending'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-red-100 text-red-800'
                        }`}>
                          {payment.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <Button variant="ghost" size="sm">View</Button>
                        {payment.status !== 'paid' && (
                          <Button variant="ghost" size="sm" className="text-green-600">Mark Paid</Button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            
            {filteredPayments.length === 0 && (
              <div className="flex flex-col items-center justify-center py-12">
                <div className="bg-gray-100 p-3 rounded-full mb-3">
                  <CreditCard className="h-6 w-6 text-gray-500" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-1">No payments found</h3>
                <p className="text-gray-500 text-center mb-4">
                  {searchQuery || statusFilter !== 'all' || typeFilter !== 'all'
                    ? 'Try adjusting your filters'
                    : 'Record your first payment to get started'}
                </p>
                <Button>
                  <Plus className="h-5 w-5 mr-1" />
                  Record Payment
                </Button>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default PaymentsPage;