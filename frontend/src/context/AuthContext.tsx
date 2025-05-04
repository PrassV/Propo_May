import React, { createContext, useContext, useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { User } from '../types';

type AuthContextType = {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signInWithGoogle: () => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  updateUserProfile: (data: Partial<User>) => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for active session on mount
    const checkSession = async () => {
      setLoading(true);
      const { data } = await supabase.auth.getSession();
      
      if (data.session) {
        // For demo purposes, create a mock user
        setUser({
          id: data.session.user.id,
          email: data.session.user.email || '',
          role: null,
          firstName: '',
          lastName: '',
          phone: '',
          createdAt: new Date().toISOString()
        });
      }
      
      setLoading(false);
    };

    checkSession();

    // Listen for auth changes
    const { data } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (event === 'SIGNED_IN' && session) {
        // For demo purposes, create a mock user
        setUser({
          id: session.user.id,
          email: session.user.email || '',
          role: null,
          firstName: '',
          lastName: '',
          phone: '',
          createdAt: new Date().toISOString()
        });
      } else if (event === 'SIGNED_OUT') {
        setUser(null);
      }
    });

    return () => {
      data.subscription.unsubscribe();
    };
  }, []);

  const signIn = async (email: string, password: string) => {
    await supabase.auth.signInWithPassword({ email, password });
  };

  const signInWithGoogle = async () => {
    await supabase.auth.signInWithOAuth({
      provider: 'google',
    });
  };

  const signUp = async (email: string, password: string) => {
    await supabase.auth.signUp({ email, password });
  };

  const signOut = async () => {
    await supabase.auth.signOut();
    setUser(null);
  };

  const updateUserProfile = async (data: Partial<User>) => {
    if (!user) return;
    
    // In a real app, we would update the user profile in Supabase
    // For demo purposes, we'll just update the local state
    setUser({ ...user, ...data });
  };

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signInWithGoogle, signUp, signOut, updateUserProfile }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}