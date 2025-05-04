import { createClient } from '@supabase/supabase-js';

// Provide development fallbacks for easier initial setup
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://example.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example-anon-key';

// If using fallbacks, provide warnings
if (!import.meta.env.VITE_SUPABASE_URL || !import.meta.env.VITE_SUPABASE_ANON_KEY) {
  console.warn(
    'Supabase credentials missing. Using development fallbacks.\n' +
    'Create .env file in project root with VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY'
  );
}

// Create a single supabase client for the entire app
export const supabase = createClient(
  supabaseUrl, 
  supabaseAnonKey
);

export default supabase; 