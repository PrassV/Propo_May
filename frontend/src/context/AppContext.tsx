import React, { createContext, useContext, useState, useEffect } from 'react';
import { generateMockData } from '../lib/utils';
import { Property, Tenant, MaintenanceRequest, Payment, DashboardStats } from '../types';

type AppContextType = {
  properties: Property[];
  tenants: Tenant[];
  maintenanceRequests: MaintenanceRequest[];
  payments: Payment[];
  dashboardStats: DashboardStats;
  isLoading: boolean;
};

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [data, setData] = useState({
    properties: [] as Property[],
    tenants: [] as Tenant[],
    maintenanceRequests: [] as MaintenanceRequest[],
    payments: [] as Payment[],
    dashboardStats: {
      totalProperties: 0,
      totalUnits: 0,
      availableUnits: 0,
      occupancyRate: 0,
      pendingMaintenanceRequests: 0,
      paymentsReceived: 0,
      upcomingPayments: 0,
      monthlyRevenue: 0,
    } as DashboardStats,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate loading data from an API
    const loadData = async () => {
      setIsLoading(true);
      try {
        // In a real app, we would fetch data from Supabase
        // For demo purposes, we'll use mock data
        const mockData = generateMockData();
        setData(mockData);
      } catch (error) {
        console.error('Error loading data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  return (
    <AppContext.Provider
      value={{
        properties: data.properties,
        tenants: data.tenants,
        maintenanceRequests: data.maintenanceRequests,
        payments: data.payments,
        dashboardStats: data.dashboardStats,
        isLoading,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}