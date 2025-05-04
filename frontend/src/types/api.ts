// User types
export interface User {
  user_id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  role: 'owner' | 'tenant' | 'maintenance' | 'admin';
  profile_picture_url?: string;
  email_verified: boolean;
  status: 'active' | 'inactive' | 'pending';
  created_at: string;
  updated_at: string;
}

export interface UserProfile extends User {
  last_login_at?: string;
}

// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
  role: 'owner' | 'tenant';
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

// Property types
export interface Property {
  property_id: string;
  owner_id: string;
  name: string;
  street: string;
  city: string;
  state: string;
  zip: string;
  country: string;
  property_type: string;
  year_built?: number;
  total_units: number;
  amenities?: string[];
  description?: string;
  status: 'active' | 'inactive' | 'deleted';
  created_at: string;
  updated_at: string;
}

export interface PropertyWithDetails extends Property {
  available_units: number;
  occupied_units: number;
  images: string[];
}

export interface PropertyCreateRequest {
  name: string;
  street: string;
  city: string;
  state: string;
  zip: string;
  country?: string;
  property_type: string;
  year_built?: number;
  total_units: number;
  amenities?: string[];
  description?: string;
}

// Unit types
export interface Unit {
  unit_id: string;
  property_id: string;
  unit_number: string;
  floor?: number;
  bedrooms: number;
  bathrooms: number;
  square_feet: number;
  rent_amount: number;
  security_deposit: number;
  status: 'available' | 'occupied' | 'maintenance' | 'reserved' | 'inactive';
  amenities?: string[];
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface UnitCreateRequest {
  property_id: string;
  unit_number: string;
  floor?: number;
  bedrooms: number;
  bathrooms: number;
  square_feet: number;
  rent_amount: number;
  security_deposit: number;
  amenities?: string[];
  description?: string;
}

// Maintenance types
export interface MaintenanceRequest {
  request_id: string;
  unit_id: string;
  tenant_id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'emergency';
  status: 'open' | 'assigned' | 'in_progress' | 'completed' | 'cancelled';
  assigned_to?: string;
  images?: string[];
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

// Dashboard types
export interface OwnerDashboard {
  total_properties: number;
  total_units: number;
  occupancy_rate: number;
  monthly_revenue: number;
  pending_maintenance: number;
  recent_activities: Activity[];
  property_overview: PropertyOverview[];
}

export interface TenantDashboard {
  unit: Unit;
  upcoming_payments: Payment[];
  maintenance_requests: MaintenanceRequest[];
  recent_activities: Activity[];
}

export interface PropertyOverview {
  property_id: string;
  name: string;
  total_units: number;
  occupied_units: number;
  total_revenue: number;
}

export interface Activity {
  id: string;
  type: 'payment' | 'maintenance' | 'lease' | 'message';
  title: string;
  description: string;
  created_at: string;
  related_id?: string;
}

export interface Payment {
  payment_id: string;
  lease_id: string;
  amount: number;
  status: 'due' | 'paid' | 'late' | 'partial';
  due_date: string;
  paid_date?: string;
  payment_method?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
} 