import React from 'react';
import { Building2, Users, Wrench, CreditCard, ArrowUp, ArrowDown } from 'lucide-react';
import Header from '../components/layout/Header';
import StatCard from '../components/dashboard/StatCard';
import PropertyList from '../components/dashboard/PropertyList';
import MaintenanceRequestList from '../components/dashboard/MaintenanceRequestList';
import PaymentsList from '../components/dashboard/PaymentsList';
import OccupancyChart from '../components/dashboard/OccupancyChart';
import { useApp } from '../context/AppContext';
import { formatCurrency } from '../lib/utils';

const DashboardPage = () => {
  const { properties, tenants, maintenanceRequests, payments, dashboardStats, isLoading } = useApp();
  
  // Filter data for display
  const activeMaintenanceRequests = maintenanceRequests.filter(
    (req) => req.status === 'new' || req.status === 'in_progress'
  );
  
  const recentPayments = payments.slice(0, 5);
  
  return (
    <div className="min-h-screen">
      <Header title="Dashboard" />
      
      <main className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Properties"
            value={dashboardStats.totalProperties}
            icon={<Building2 className="w-6 h-6" />}
            trend={{ value: 8.2, isPositive: true }}
          />
          <StatCard
            title="Total Tenants"
            value={tenants.length}
            icon={<Users className="w-6 h-6" />}
            trend={{ value: 12.5, isPositive: true }}
          />
          <StatCard
            title="Maintenance Requests"
            value={activeMaintenanceRequests.length}
            icon={<Wrench className="w-6 h-6" />}
            trend={{ value: 2.4, isPositive: false }}
          />
          <StatCard
            title="Monthly Revenue"
            value={formatCurrency(dashboardStats.monthlyRevenue)}
            icon={<CreditCard className="w-6 h-6" />}
            trend={{ value: 4.1, isPositive: true }}
          />
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-1">
            <OccupancyChart
              occupied={dashboardStats.totalUnits - dashboardStats.availableUnits}
              available={dashboardStats.availableUnits}
            />
          </div>
          <div className="lg:col-span-2">
            <PropertyList properties={properties} />
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <MaintenanceRequestList requests={activeMaintenanceRequests} />
          <PaymentsList payments={recentPayments} />
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;