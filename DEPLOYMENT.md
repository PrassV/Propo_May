# Property Management Portal Deployment Guide

This guide explains how to deploy the Property Management Portal backend to Railway.

## Prerequisites

1. A Railway account (https://railway.app/)
2. A Supabase account and project (https://supabase.com/)
3. Git repository with your code

## Environment Variables

The following environment variables need to be set in Railway:

```
# Deployment
ENVIRONMENT=production
DEBUG=False
BASE_URL=https://propomay-production.up.railway.app

# Security
JWT_SECRET=your-secure-random-secret

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# Database (optional - Railway will provide this if you add a PostgreSQL database)
DATABASE_URL=postgresql+asyncpg://postgres:password@railway-postgres-instance:5432/railway

# Email (optional)
RESEND_API_KEY=your-resend-api-key
```

## Deployment Steps

1. **Create a new project in Railway**

   - Go to https://railway.app/dashboard
   - Click "New Project" → "Deploy from GitHub repo"
   - Connect your GitHub account and select your repository
   - Click "Deploy Now"

2. **Configure Environment Variables**

   - In your Railway project, go to the "Variables" tab
   - Add all the required environment variables listed above
   - Make sure to set a strong `JWT_SECRET` value

3. **Add PostgreSQL (Optional)**

   - If you want to use Railway's PostgreSQL:
     - Click "New" → "Database" → "PostgreSQL"
     - Railway will automatically add the `DATABASE_URL` to your project

4. **Verify Deployment**

   - Once deployed, Railway will provide a URL for your application
   - Visit `https://your-railway-url.railway.app/` to see the welcome message
   - Visit `https://your-railway-url.railway.app/docs` to see the API documentation

## Supabase Configuration

1. **Enable Authentication**

   - In your Supabase project, go to Authentication → Settings
   - Enable Email and Password sign-in
   - Configure any other authentication providers you want to use

2. **CORS Configuration**

   - In your Supabase project, go to Authentication → URL Configuration
   - Add your Railway URL and your frontend URL(s) to the Site URL and additional redirect URLs

3. **Create Database Tables**

   - Use the SQL Editor or Database UI to create your required tables
   - Make sure the database schema matches what your application expects

## Updating Your Deployment

Railway will automatically redeploy your application when you push changes to the connected GitHub repository.

## Troubleshooting

- **Check Logs**: In your Railway project, go to the "Logs" tab to see application logs
- **Health Check**: Visit `https://your-railway-url.railway.app/health` to verify the API is running
- **Database Connection**: Ensure your application can connect to the database by checking logs
- **Supabase Connection**: Verify the Supabase URL and keys are correct 