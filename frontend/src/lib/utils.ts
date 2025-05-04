import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Utility for merging Tailwind classes
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Format currency
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
}

// Format date
export function formatDate(date: string): string {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

// Calculate days remaining in lease
export function daysRemaining(endDate: string): number {
  const end = new Date(endDate);
  const today = new Date();
  const diffTime = end.getTime() - today.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

// Calculate occupancy rate
export function calculateOccupancyRate(totalUnits: number, occupiedUnits: number): number {
  if (totalUnits === 0) return 0;
  return (occupiedUnits / totalUnits) * 100;
}

// Generate mock data for demo purposes
export function generateMockData() {
  return {
    properties: Array(5).fill(null).map((_, i) => ({
      id: `prop-${i + 1}`,
      name: `Property ${i + 1}`,
      address: `${1000 + i} Main Street`,
      city: 'Cityville',
      state: 'ST',
      zipCode: '12345',
      type: ['apartment', 'house', 'condo', 'commercial'][i % 4] as 'apartment' | 'house' | 'condo' | 'commercial',
      units: 10 + i,
      availableUnits: i + 1,
      imageUrl: `https://images.pexels.com/photos/${2121121 + i * 100000}/pexels-photo-${2121121 + i * 100000}.jpeg?auto=compress&cs=tinysrgb&w=600`,
      ownerId: 'user-1',
    })),
    tenants: Array(8).fill(null).map((_, i) => ({
      id: `tenant-${i + 1}`,
      userId: `user-${i + 10}`,
      propertyId: `prop-${(i % 5) + 1}`,
      unitNumber: `${101 + i}`,
      leaseStart: new Date(2023, 0, 1).toISOString(),
      leaseEnd: new Date(2024, 0, 1).toISOString(),
      rentAmount: 1000 + (i * 100),
      securityDeposit: 1000,
      status: ['active', 'active', 'active', 'pending'][i % 4] as 'active' | 'pending' | 'past',
    })),
    maintenanceRequests: Array(6).fill(null).map((_, i) => ({
      id: `req-${i + 1}`,
      tenantId: `tenant-${(i % 8) + 1}`,
      propertyId: `prop-${(i % 5) + 1}`,
      unitNumber: `${101 + (i % 8)}`,
      title: ['Leaking faucet', 'Broken AC', 'Electrical issue', 'Clogged drain', 'Broken window', 'Pest control'][i],
      description: `Description for maintenance request ${i + 1}`,
      priority: ['low', 'medium', 'high', 'emergency'][i % 4] as 'low' | 'medium' | 'high' | 'emergency',
      status: ['new', 'in_progress', 'completed', 'new'][i % 4] as 'new' | 'in_progress' | 'completed' | 'cancelled',
      createdAt: new Date(2023, 5, i + 1).toISOString(),
      updatedAt: new Date(2023, 5, i + 3).toISOString(),
    })),
    payments: Array(10).fill(null).map((_, i) => ({
      id: `payment-${i + 1}`,
      tenantId: `tenant-${(i % 8) + 1}`,
      propertyId: `prop-${(i % 5) + 1}`,
      amount: 1000 + (i * 50),
      dueDate: new Date(2023, 5, 1 + i).toISOString(),
      paidDate: i < 6 ? new Date(2023, 5, 1 + i).toISOString() : null,
      status: i < 6 ? 'paid' : i < 8 ? 'pending' : 'overdue' as 'pending' | 'paid' | 'overdue',
      type: ['rent', 'rent', 'fee', 'deposit'][i % 4] as 'rent' | 'deposit' | 'fee' | 'other',
    })),
    dashboardStats: {
      totalProperties: 5,
      totalUnits: 65,
      availableUnits: 15,
      occupancyRate: 76.9,
      pendingMaintenanceRequests: 4,
      paymentsReceived: 6,
      upcomingPayments: 4,
      monthlyRevenue: 8200,
    }
  };
}