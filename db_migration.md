-- Property Management Portal Database Schema Migration
-- This script creates all tables, views, and indexes for the property management portal

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if they exist (in reverse dependency order)
DO $$ 
BEGIN
    -- Drop views first
    DROP VIEW IF EXISTS financial_summary_view;
    DROP VIEW IF EXISTS occupancy_status_view;
    DROP VIEW IF EXISTS payment_history_view;
    DROP VIEW IF EXISTS maintenance_requests_view;
    DROP VIEW IF EXISTS active_tenants_view;

    -- Drop tables in reverse dependency order
    DROP TABLE IF EXISTS listing_photos;
    DROP TABLE IF EXISTS unit_listings;
    DROP TABLE IF EXISTS tenant_invitations;
    DROP TABLE IF EXISTS user_notification_preferences;
    DROP TABLE IF EXISTS market_analysis;
    DROP TABLE IF EXISTS report_properties;
    DROP TABLE IF EXISTS reports;
    DROP TABLE IF EXISTS insurance_policies;
    DROP TABLE IF EXISTS tasks;
    DROP TABLE IF EXISTS notification_settings;
    DROP TABLE IF EXISTS notifications;
    DROP TABLE IF EXISTS announcement_attachments;
    DROP TABLE IF EXISTS announcement_properties;
    DROP TABLE IF EXISTS announcements;
    DROP TABLE IF EXISTS message_attachments;
    DROP TABLE IF EXISTS message_recipients;
    DROP TABLE IF EXISTS messages;
    DROP TABLE IF EXISTS documents;
    DROP TABLE IF EXISTS inspection_images;
    DROP TABLE IF EXISTS inspections;
    DROP TABLE IF EXISTS work_orders;
    DROP TABLE IF EXISTS vendors;
    DROP TABLE IF EXISTS maintenance_reviews;
    DROP TABLE IF EXISTS maintenance_staff_properties;
    DROP TABLE IF EXISTS maintenance_notes;
    DROP TABLE IF EXISTS maintenance_request_images;
    DROP TABLE IF EXISTS maintenance_requests;
    DROP TABLE IF EXISTS expenses;
    DROP TABLE IF EXISTS invoices;
    DROP TABLE IF EXISTS payments;
    DROP TABLE IF EXISTS tenant_info;
    DROP TABLE IF EXISTS leases;
    DROP TABLE IF EXISTS applications;
    DROP TABLE IF EXISTS unit_images;
    DROP TABLE IF EXISTS units;
    DROP TABLE IF EXISTS property_images;
    DROP TABLE IF EXISTS properties;
    DROP TABLE IF EXISTS system_settings;
    DROP TABLE IF EXISTS users;
END $$;

-- Create tables in order of dependency

-- 1. Users
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(50),
    role VARCHAR(20) NOT NULL CHECK (role IN ('owner', 'tenant', 'maintenance', 'admin')),
    profile_picture_url VARCHAR(255),
    email_verified BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'pending')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ
);

CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_email ON users(email);

-- 2. Properties
CREATE TABLE properties (
    property_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL REFERENCES users(user_id),
    name VARCHAR(255) NOT NULL,
    street VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip VARCHAR(20) NOT NULL,
    country VARCHAR(50) DEFAULT 'USA',
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    property_type VARCHAR(50) NOT NULL,
    year_built INTEGER,
    total_units INTEGER NOT NULL,
    amenities TEXT[] DEFAULT '{}',
    description TEXT,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'deleted')),
    tax_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_properties_owner ON properties(owner_id);
CREATE INDEX idx_properties_location ON properties(city, state);

-- 3. Property_Images
CREATE TABLE property_images (
    image_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID NOT NULL REFERENCES properties(property_id) ON DELETE CASCADE,
    image_url VARCHAR(255) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    display_order INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_property_images_property ON property_images(property_id);

-- 4. Units
CREATE TABLE units (
    unit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID NOT NULL REFERENCES properties(property_id) ON DELETE CASCADE,
    unit_number VARCHAR(50) NOT NULL,
    floor INTEGER,
    bedrooms DECIMAL(3, 1) NOT NULL,
    bathrooms DECIMAL(3, 1) NOT NULL,
    square_feet INTEGER NOT NULL,
    rent_amount DECIMAL(10, 2) NOT NULL,
    security_deposit DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available', 'occupied', 'maintenance', 'reserved', 'inactive')),
    amenities TEXT[] DEFAULT '{}',
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(property_id, unit_number)
);

CREATE INDEX idx_units_property ON units(property_id);
CREATE INDEX idx_units_status ON units(status);
CREATE INDEX idx_units_bedrooms ON units(bedrooms);

-- 5. Unit_Images
CREATE TABLE unit_images (
    image_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    unit_id UUID NOT NULL REFERENCES units(unit_id) ON DELETE CASCADE,
    image_url VARCHAR(255) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    display_order INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_unit_images_unit ON unit_images(unit_id);

-- 6. Applications
CREATE TABLE applications (
    application_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    unit_id UUID NOT NULL REFERENCES units(unit_id),
    user_id UUID REFERENCES users(user_id),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    current_street VARCHAR(255) NOT NULL,
    current_city VARCHAR(100) NOT NULL,
    current_state VARCHAR(50) NOT NULL,
    current_zip VARCHAR(20) NOT NULL,
    current_country VARCHAR(50) DEFAULT 'USA',
    employer VARCHAR(255),
    position VARCHAR(255),
    monthly_income DECIMAL(10, 2),
    employment_start_date DATE,
    emergency_contact_name VARCHAR(255),
    emergency_contact_relationship VARCHAR(100),
    emergency_contact_phone VARCHAR(50),
    move_in_date DATE NOT NULL,
    lease_term INTEGER NOT NULL,
    has_pets BOOLEAN DEFAULT FALSE,
    pet_details JSONB,
    vehicle_info JSONB,
    has_bankruptcy BOOLEAN DEFAULT FALSE,
    has_eviction BOOLEAN DEFAULT FALSE,
    has_criminal_record BOOLEAN DEFAULT FALSE,
    additional_occupants JSONB,
    references JSONB,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'withdrawn')),
    admin_notes TEXT,
    notes TEXT,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_applications_unit ON applications(unit_id);
CREATE INDEX idx_applications_user ON applications(user_id);
CREATE INDEX idx_applications_status ON applications(status);

-- 7. Leases
CREATE TABLE leases (
    lease_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    unit_id UUID NOT NULL REFERENCES units(unit_id),
    tenant_id UUID NOT NULL REFERENCES users(user_id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    rent_amount DECIMAL(10, 2) NOT NULL,
    security_deposit DECIMAL(10, 2) NOT NULL,
    payment_day INTEGER NOT NULL CHECK (payment_day BETWEEN 1 AND 31),
    late_fee JSONB,
    utilities_included TEXT[] DEFAULT '{}',
    pets_allowed BOOLEAN DEFAULT FALSE,
    pet_deposit DECIMAL(10, 2) DEFAULT 0,
    smoking_allowed BOOLEAN DEFAULT FALSE,
    special_terms TEXT,
    auto_renew BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'expired', 'terminated', 'renewed')),
    document_url VARCHAR(255),
    previous_lease_id UUID REFERENCES leases(lease_id),
    termination_date DATE,
    termination_reason TEXT,
    fees_applied DECIMAL(10, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_leases_unit ON leases(unit_id);
CREATE INDEX idx_leases_tenant ON leases(tenant_id);
CREATE INDEX idx_leases_status ON leases(status);
CREATE INDEX idx_leases_dates ON leases(start_date, end_date);

-- 8. Tenant_Info
CREATE TABLE tenant_info (
    tenant_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    lease_id UUID REFERENCES leases(lease_id),
    move_in_date DATE,
    emergency_contact_name VARCHAR(255),
    emergency_contact_relationship VARCHAR(100),
    emergency_contact_phone VARCHAR(50),
    vehicle_info JSONB,
    additional_occupants JSONB,
    has_pets BOOLEAN DEFAULT FALSE,
    pet_details JSONB,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'former')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tenant_info_lease ON tenant_info(lease_id);

-- 9. Payments
CREATE TABLE payments (
    payment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lease_id UUID NOT NULL REFERENCES leases(lease_id),
    tenant_id UUID NOT NULL REFERENCES users(user_id),
    amount DECIMAL(10, 2) NOT NULL,
    payment_date DATE NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    transaction_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'completed' CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    notes TEXT,
    receipt_url VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_payments_lease ON payments(lease_id);
CREATE INDEX idx_payments_tenant ON payments(tenant_id);
CREATE INDEX idx_payments_date ON payments(payment_date);

-- 10. Invoices
CREATE TABLE invoices (
    invoice_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lease_id UUID NOT NULL REFERENCES leases(lease_id),
    tenant_id UUID NOT NULL REFERENCES users(user_id),
    amount DECIMAL(10, 2) NOT NULL,
    due_date DATE NOT NULL,
    description TEXT NOT NULL,
    line_items JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'partial', 'overdue', 'cancelled')),
    payment_id UUID REFERENCES payments(payment_id),
    invoice_url VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_invoices_lease ON invoices(lease_id);
CREATE INDEX idx_invoices_tenant ON invoices(tenant_id);
CREATE INDEX idx_invoices_due_date ON invoices(due_date);
CREATE INDEX idx_invoices_status ON invoices(status);

-- 12. Vendors (needs to be defined before expenses)
CREATE TABLE vendors (
    vendor_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50) NOT NULL,
    street VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip VARCHAR(20),
    country VARCHAR(50) DEFAULT 'USA',
    services TEXT[] DEFAULT '{}',
    insurance_info JSONB,
    tax_id VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_vendors_services ON vendors USING GIN(services);
CREATE INDEX idx_vendors_location ON vendors(city, state);

-- 11. Expenses
CREATE TABLE expenses (
    expense_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID NOT NULL REFERENCES properties(property_id),
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50),
    description TEXT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    date DATE NOT NULL,
    payment_method VARCHAR(50),
    vendor_id UUID REFERENCES vendors(vendor_id),
    receipt_url VARCHAR(255),
    expense_type VARCHAR(20) NOT NULL CHECK (expense_type IN ('one-time', 'recurring')),
    frequency VARCHAR(20),
    start_date DATE,
    end_date DATE,
    next_occurrence DATE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_expenses_property ON expenses(property_id);
CREATE INDEX idx_expenses_category ON expenses(category);
CREATE INDEX idx_expenses_date ON expenses(date);
CREATE INDEX idx_expenses_type ON expenses(expense_type);

-- 12. Maintenance_Requests
CREATE TABLE maintenance_requests (
    request_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    unit_id UUID NOT NULL REFERENCES units(unit_id),
    tenant_id UUID NOT NULL REFERENCES users(user_id),
    property_id UUID NOT NULL REFERENCES properties(property_id),
    category VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'emergency')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'assigned', 'scheduled', 'in_progress', 'completed', 'cancelled')),
    preferred_time TEXT[] DEFAULT '{}',
    allow_entry_without_tenant BOOLEAN DEFAULT FALSE,
    has_pets BOOLEAN DEFAULT FALSE,
    assigned_to UUID REFERENCES users(user_id),
    scheduled_date DATE,
    scheduled_time VARCHAR(50),
    estimated_cost DECIMAL(10, 2),
    completion_notes TEXT,
    materials_used TEXT,
    labor_hours DECIMAL(5, 2),
    total_cost DECIMAL(10, 2),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_maintenance_requests_unit ON maintenance_requests(unit_id);
CREATE INDEX idx_maintenance_requests_tenant ON maintenance_requests(tenant_id);
CREATE INDEX idx_maintenance_requests_property ON maintenance_requests(property_id);
CREATE INDEX idx_maintenance_requests_assigned_to ON maintenance_requests(assigned_to);
CREATE INDEX idx_maintenance_requests_status ON maintenance_requests(status);

-- 13. Maintenance_Request_Images
CREATE TABLE maintenance_request_images (
    image_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID NOT NULL REFERENCES maintenance_requests(request_id) ON DELETE CASCADE,
    image_url VARCHAR(255) NOT NULL,
    image_type VARCHAR(20) DEFAULT 'issue' CHECK (image_type IN ('issue', 'completion')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_maintenance_request_images_request ON maintenance_request_images(request_id);

-- 14. Maintenance_Notes
CREATE TABLE maintenance_notes (
    note_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID NOT NULL REFERENCES maintenance_requests(request_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id),
    note TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_maintenance_notes_request ON maintenance_notes(request_id);

-- 15. Maintenance_Staff_Properties
CREATE TABLE maintenance_staff_properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id),
    property_id UUID NOT NULL REFERENCES properties(property_id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, property_id)
);

CREATE INDEX idx_maintenance_staff_properties_user ON maintenance_staff_properties(user_id);
CREATE INDEX idx_maintenance_staff_properties_property ON maintenance_staff_properties(property_id);

-- 16. Maintenance_Reviews
CREATE TABLE maintenance_reviews (
    review_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID NOT NULL REFERENCES maintenance_requests(request_id) UNIQUE,
    tenant_id UUID NOT NULL REFERENCES users(user_id),
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comments TEXT,
    response_time_rating INTEGER CHECK (response_time_rating BETWEEN 1 AND 5),
    quality_rating INTEGER CHECK (quality_rating BETWEEN 1 AND 5),
    professionalism_rating INTEGER CHECK (professionalism_rating BETWEEN 1 AND 5),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_maintenance_reviews_request ON maintenance_reviews(request_id);
CREATE INDEX idx_maintenance_reviews_tenant ON maintenance_reviews(tenant_id);

-- 17. Work_Orders
CREATE TABLE work_orders (
    work_order_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    maintenance_request_id UUID REFERENCES maintenance_requests(request_id),
    vendor_id UUID NOT NULL REFERENCES vendors(vendor_id),
    property_id UUID NOT NULL REFERENCES properties(property_id),
    unit_id UUID REFERENCES units(unit_id),
    description TEXT NOT NULL,
    estimated_cost DECIMAL(10, 2),
    scheduled_date DATE,
    scheduled_time VARCHAR(50),
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'emergency')),
    status VARCHAR(20) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled')),
    completion_date DATE,
    actual_cost DECIMAL(10, 2),
    labor_hours DECIMAL(5, 2),
    materials_used TEXT,
    notes TEXT,
    invoice_number VARCHAR(100),
    invoice_url VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_work_orders_maintenance_request ON work_orders(maintenance_request_id);
CREATE INDEX idx_work_orders_vendor ON work_orders(vendor_id);
CREATE INDEX idx_work_orders_property ON work_orders(property_id);
CREATE INDEX idx_work_orders_unit ON work_orders(unit_id);
CREATE INDEX idx_work_orders_status ON work_orders(status);

-- 18. Inspections
CREATE TABLE inspections (
    inspection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    unit_id UUID NOT NULL REFERENCES units(unit_id),
    property_id UUID NOT NULL REFERENCES properties(property_id),
    type VARCHAR(50) NOT NULL CHECK (type IN ('move_in', 'move_out', 'routine', 'special')),
    scheduled_date DATE NOT NULL,
    scheduled_time VARCHAR(50),
    inspector_id UUID NOT NULL REFERENCES users(user_id),
    status VARCHAR(20) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'cancelled')),
    condition VARCHAR(20),
    notes TEXT,
    tenant_notified BOOLEAN DEFAULT FALSE,
    items JSONB,
    report_url VARCHAR(255),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_inspections_unit ON inspections(unit_id);
CREATE INDEX idx_inspections_property ON inspections(property_id);
CREATE INDEX idx_inspections_inspector ON inspections(inspector_id);
CREATE INDEX idx_inspections_status ON inspections(status);

-- 19. Inspection_Images
CREATE TABLE inspection_images (
    image_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inspection_id UUID NOT NULL REFERENCES inspections(inspection_id) ON DELETE CASCADE,
    image_url VARCHAR(255) NOT NULL,
    category VARCHAR(50),
    item VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_inspection_images_inspection ON inspection_images(inspection_id);

-- 20. Documents
CREATE TABLE documents (
    document_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    associated_id UUID,
    associated_type VARCHAR(50) NOT NULL,
    description TEXT,
    file_type VARCHAR(100) NOT NULL,
    file_size INTEGER NOT NULL,
    uploaded_by UUID NOT NULL REFERENCES users(user_id),
    access_roles TEXT[] DEFAULT '{}',
    url VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_documents_category ON documents(category);
CREATE INDEX idx_documents_associated ON documents(associated_id, associated_type);
CREATE INDEX idx_documents_uploaded_by ON documents(uploaded_by);
CREATE INDEX idx_documents_access_roles ON documents USING GIN(access_roles);

-- 21. Messages
CREATE TABLE messages (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sender_id UUID NOT NULL REFERENCES users(user_id),
    subject VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    sent_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_messages_sender ON messages(sender_id);

-- 22. Message_Recipients
CREATE TABLE message_recipients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID NOT NULL REFERENCES messages(message_id) ON DELETE CASCADE,
    recipient_id UUID NOT NULL REFERENCES users(user_id),
    read_status BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    folder VARCHAR(20) DEFAULT 'inbox' CHECK (folder IN ('inbox', 'sent', 'archived')),
    archived_at TIMESTAMPTZ,
    UNIQUE(message_id, recipient_id)
);

CREATE INDEX idx_message_recipients_message ON message_recipients(message_id);
CREATE INDEX idx_message_recipients_recipient ON message_recipients(recipient_id);
CREATE INDEX idx_message_recipients_folder ON message_recipients(folder);

-- 23. Message_Attachments
CREATE TABLE message_attachments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID NOT NULL REFERENCES messages(message_id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(document_id),
    UNIQUE(message_id, document_id)
);

CREATE INDEX idx_message_attachments_message ON message_attachments(message_id);

-- 24. Announcements
CREATE TABLE announcements (
    announcement_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    importance VARCHAR(20) DEFAULT 'normal' CHECK (importance IN ('low', 'normal', 'high')),
    created_by UUID NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_announcements_dates ON announcements(start_date, end_date);
CREATE INDEX idx_announcements_created_by ON announcements(created_by);

-- 25. Announcement_Properties
CREATE TABLE announcement_properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    announcement_id UUID NOT NULL REFERENCES announcements(announcement_id) ON DELETE CASCADE,
    property_id UUID NOT NULL REFERENCES properties(property_id),
    UNIQUE(announcement_id, property_id)
);

CREATE INDEX idx_announcement_properties_announcement ON announcement_properties(announcement_id);
CREATE INDEX idx_announcement_properties_property ON announcement_properties(property_id);

-- 26. Announcement_Attachments
CREATE TABLE announcement_attachments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    announcement_id UUID NOT NULL REFERENCES announcements(announcement_id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(document_id),
    UNIQUE(announcement_id, document_id)
);

CREATE INDEX idx_announcement_attachments_announcement ON announcement_attachments(announcement_id);

-- 27. Notifications
CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id),
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    related_entity_type VARCHAR(50),
    related_entity_id UUID,
    read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(read);
CREATE INDEX idx_notifications_entity ON notifications(related_entity_type, related_entity_id);

-- 28. System_Settings
CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    company JSONB NOT NULL,
    payment_settings JSONB NOT NULL,
    notification_settings JSONB NOT NULL,
    document_templates JSONB NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by UUID REFERENCES users(user_id)
);

-- 29. Tasks
CREATE TABLE tasks (
    task_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE,
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    created_by UUID NOT NULL REFERENCES users(user_id),
    assigned_to UUID NOT NULL REFERENCES users(user_id),
    associated_entity_type VARCHAR(50),
    associated_entity_id UUID,
    reminder_date DATE,
    completion_notes TEXT,
    completed_at TIMESTAMPTZ,
    completed_by UUID REFERENCES users(user_id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tasks_created_by ON tasks(created_by);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_associated_entity ON tasks(associated_entity_type, associated_entity_id);

-- 30. Insurance_Policies
CREATE TABLE insurance_policies (
    insurance_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID NOT NULL REFERENCES properties(property_id),
    insurance_type VARCHAR(50) NOT NULL,
    provider VARCHAR(255) NOT NULL,
    policy_number VARCHAR(100) NOT NULL,
    coverage_amount DECIMAL(12, 2) NOT NULL,
    deductible DECIMAL(10, 2) NOT NULL,
    premium DECIMAL(10, 2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    coverage_details JSONB,
    agent JSONB,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'expired', 'cancelled')),
    policy_document_url VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_insurance_policies_property ON insurance_policies(property_id);
CREATE INDEX idx_insurance_policies_dates ON insurance_policies(start_date, end_date);
CREATE INDEX idx_insurance_policies_status ON insurance_policies(status);

-- 31. Reports
CREATE TABLE reports (
    report_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(50) NOT NULL,
    subtype VARCHAR(50),
    parameters JSONB NOT NULL,
    summary JSONB,
    report_url VARCHAR(255) NOT NULL,
    created_by UUID NOT NULL REFERENCES users(user_id),
    generated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_reports_type ON reports(type, subtype);
CREATE INDEX idx_reports_created_by ON reports(created_by);

-- 32. Report_Properties
CREATE TABLE report_properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id UUID NOT NULL REFERENCES reports(report_id) ON DELETE CASCADE,
    property_id UUID NOT NULL REFERENCES properties(property_id),
    UNIQUE(report_id, property_id)
);

CREATE INDEX idx_report_properties_report ON report_properties(report_id);
CREATE INDEX idx_report_properties_property ON report_properties(property_id);

-- 33. Market_Analysis
CREATE TABLE market_analysis (
    analysis_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID NOT NULL REFERENCES properties(property_id),
    analysis_date DATE NOT NULL,
    comparable_properties JSONB NOT NULL,
    suggested_rent_adjustments JSONB NOT NULL,
    notes TEXT,
    created_by UUID NOT NULL REFERENCES users(user_id),
    report_url VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_market_analysis_property ON market_analysis(property_id);
CREATE INDEX idx_market_analysis_date ON market_analysis(analysis_date);

-- 34. User_Notification_Preferences
CREATE TABLE user_notification_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    email_notifications JSONB NOT NULL,
    sms_notifications JSONB NOT NULL,
    push_notifications JSONB NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 35. Tenant_Invitations
CREATE TABLE tenant_invitations (
    invitation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(50),
    unit_id UUID NOT NULL REFERENCES units(unit_id),
    message TEXT,
    status VARCHAR(20) DEFAULT 'sent' CHECK (status IN ('sent', 'accepted', 'expired')),
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_by UUID NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tenant_invitations_email ON tenant_invitations(email);
CREATE INDEX idx_tenant_invitations_unit ON tenant_invitations(unit_id);
CREATE INDEX idx_tenant_invitations_status ON tenant_invitations(status);

-- 36. Unit_Listings
CREATE TABLE unit_listings (
    listing_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    unit_id UUID NOT NULL REFERENCES units(unit_id) UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    monthly_rent DECIMAL(10, 2) NOT NULL,
    security_deposit DECIMAL(10, 2) NOT NULL,
    available_date DATE NOT NULL,
    lease_terms INTEGER[] DEFAULT '{}',
    pet_policy JSONB,
    utilities_included TEXT[] DEFAULT '{}',
    amenities_highlight TEXT[] DEFAULT '{}',
    application_fee DECIMAL(7, 2),
    video_tour_url VARCHAR(255),
    showing_instructions TEXT,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'rented')),
    public_url VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_unit_listings_unit ON unit_listings(unit_id);
CREATE INDEX idx_unit_listings_status ON unit_listings(status);
CREATE INDEX idx_unit_listings_rent ON unit_listings(monthly_rent);
CREATE INDEX idx_unit_listings_available_date ON unit_listings(available_date);

-- 37. Listing_Photos
CREATE TABLE listing_photos (
    photo_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    listing_id UUID NOT NULL REFERENCES unit_listings(listing_id) ON DELETE CASCADE,
    image_url VARCHAR(255) NOT NULL,
    is_featured BOOLEAN DEFAULT FALSE,
    display_order INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_listing_photos_listing ON listing_photos(listing_id);

-- Create Views

-- 1. View for Active Tenants with Unit and Property Info
CREATE VIEW active_tenants_view AS
SELECT 
    u.user_id, u.first_name, u.last_name, u.email, u.phone,
    ti.move_in_date, ti.status as tenant_status,
    l.lease_id, l.start_date, l.end_date, l.rent_amount,
    un.unit_id, un.unit_number, un.bedrooms, un.bathrooms,
    p.property_id, p.name as property_name, p.street, p.city, p.state, p.zip
FROM 
    users u
JOIN 
    tenant_info ti ON u.user_id = ti.tenant_id
JOIN 
    leases l ON ti.lease_id = l.lease_id
JOIN 
    units un ON l.unit_id = un.unit_id
JOIN 
    properties p ON un.property_id = p.property_id
WHERE 
    u.role = 'tenant' 
    AND ti.status = 'active' 
    AND l.status = 'active';

-- 2. View for Maintenance Requests with Related Info
CREATE VIEW maintenance_requests_view AS
SELECT 
    mr.request_id, mr.title, mr.description, mr.category, mr.priority, mr.status,
    mr.created_at, mr.updated_at, mr.scheduled_date, mr.completed_at,
    u.unit_id, u.unit_number,
    p.property_id, p.name as property_name,
    tenant.user_id as tenant_id, tenant.first_name as tenant_first_name, tenant.last_name as tenant_last_name,
    staff.user_id as staff_id, staff.first_name as staff_first_name, staff.last_name as staff_last_name
FROM 
    maintenance_requests mr
JOIN 
    units u ON mr.unit_id = u.unit_id
JOIN 
    properties p ON mr.property_id = p.property_id
JOIN 
    users tenant ON mr.tenant_id = tenant.user_id
LEFT JOIN 
    users staff ON mr.assigned_to = staff.user_id;

-- 3. View for Payment History
CREATE VIEW payment_history_view AS
SELECT 
    p.payment_id, p.amount, p.payment_date, p.payment_method, p.status,
    l.lease_id, l.rent_amount,
    tenant.user_id as tenant_id, tenant.first_name as tenant_first_name, tenant.last_name as tenant_last_name,
    u.unit_id, u.unit_number,
    prop.property_id, prop.name as property_name
FROM 
    payments p
JOIN 
    leases l ON p.lease_id = l.lease_id
JOIN 
    users tenant ON p.tenant_id = tenant.user_id
JOIN 
    units u ON l.unit_id = u.unit_id
JOIN 
    properties prop ON u.property_id = prop.property_id;

-- 4. View for Occupancy Status
CREATE VIEW occupancy_status_view AS
SELECT 
    p.property_id, p.name as property_name,
    COUNT(u.unit_id) as total_units,
    SUM(CASE WHEN u.status = 'occupied' THEN 1 ELSE 0 END) as occupied_units,
    SUM(CASE WHEN u.status = 'available' THEN 1 ELSE 0 END) as available_units,
    SUM(CASE WHEN u.status = 'maintenance' THEN 1 ELSE 0 END) as maintenance_units,
    ROUND((SUM(CASE WHEN u.status = 'occupied' THEN 1 ELSE 0 END)::DECIMAL / COUNT(u.unit_id)) * 100, 2) as occupancy_rate
FROM 
    properties p
JOIN 
    units u ON p.property_id = u.property_id
GROUP BY 
    p.property_id, p.name;

-- 5. View for Financial Summary
CREATE VIEW financial_summary_view AS
SELECT 
    p.property_id, p.name as property_name,
    DATE_TRUNC('month', payment_date) as month,
    SUM(pay.amount) as total_income,
    SUM(CASE WHEN e.expense_id IS NOT NULL THEN e.amount ELSE 0 END) as total_expenses,
    SUM(pay.amount) - SUM(CASE WHEN e.expense_id IS NOT NULL THEN e.amount ELSE 0 END) as net_income
FROM 
    properties p
LEFT JOIN 
    units u ON p.property_id = u.property_id
LEFT JOIN 
    leases l ON u.unit_id = l.unit_id
LEFT JOIN 
    payments pay ON l.lease_id = pay.lease_id
LEFT JOIN 
    expenses e ON p.property_id = e.property_id AND DATE_TRUNC('month', pay.payment_date) = DATE_TRUNC('month', e.date)
WHERE 
    pay.status = 'completed'
GROUP BY 
    p.property_id, p.name, DATE_TRUNC('month', payment_date);

-- Insert initial admin user with hashed password ('admin123')
INSERT INTO users (
    email, 
    password_hash, 
    first_name, 
    last_name, 
    phone, 
    role, 
    email_verified, 
    status
) VALUES (
    'admin@example.com', 
    '$2b$12$OvmnQB4n.vr5rptqpiYGO.yw54lZQIyFLy6qD5L/.5OiIfKlU.W32', -- Hashed 'admin123'
    'System', 
    'Administrator', 
    '555-123-4567', 
    'admin', 
    TRUE, 
    'active'
);

-- Insert initial system settings
INSERT INTO system_settings (
    company, 
    payment_settings, 
    notification_settings, 
    document_templates
) VALUES (
    '{"name": "ABC Property Management", "address": {"street": "789 Business Blvd", "city": "Los Angeles", "state": "CA", "zip": "90001", "country": "USA"}, "phone": "555-789-0123", "email": "info@abcproperties.com", "website": "https://www.abcproperties.com"}',
    '{"payment_methods": ["credit_card", "bank_transfer", "check"], "payment_processors": ["stripe", "paypal"], "late_fee_defaults": {"grace_period_days": 5, "percentage": 5, "minimum_amount": 50.00}}',
    '{"email_notifications": true, "sms_notifications": true, "push_notifications": true, "default_maintenance_notifications": ["assigned", "scheduled", "completed"]}',
    '[{"template_id": "template_standard_residential", "name": "Standard Residential Lease", "document_type": "lease"}]'
);

-- Output confirmation
SELECT 'Property Management Portal database schema successfully created!' as result;