export interface User {
  id: string;
  email: string;
  role: 'owner' | 'tenant' | null;
  firstName: string;
  lastName: string;
  phone: string;
  avatarUrl?: string;
  createdAt: string;
}

export interface Property {
  id: string;
  name: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
  type: 'apartment' | 'house' | 'condo' | 'commercial';
  units: number;
  availableUnits: number;
  imageUrl: string;
  ownerId: string;
}

export interface Tenant {
  id: string;
  userId: string;
  propertyId: string;
  unitNumber: string;
  leaseStart: string;
  leaseEnd: string;
  rentAmount: number;
  securityDeposit: number;
  status: 'active' | 'pending' | 'past';
}

export interface MaintenanceRequest {
  id: string;
  tenantId: string;
  propertyId: string;
  unitNumber: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'emergency';
  status: 'new' | 'in_progress' | 'completed' | 'cancelled';
  createdAt: string;
  updatedAt: string;
}

export interface Payment {
  id: string;
  tenantId: string;
  propertyId: string;
  amount: number;
  dueDate: string;
  paidDate: string | null;
  status: 'pending' | 'paid' | 'overdue';
  type: 'rent' | 'deposit' | 'fee' | 'other';
}

export interface DashboardStats {
  totalProperties: number;
  totalUnits: number;
  availableUnits: number;
  occupancyRate: number;
  pendingMaintenanceRequests: number;
  paymentsReceived: number;
  upcomingPayments: number;
  monthlyRevenue: number;
}