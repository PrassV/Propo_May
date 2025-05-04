import React from 'react';
import Navbar from '../components/landing/Navbar';
import Hero from '../components/landing/Hero';
import Features from '../components/landing/Features';
import Testimonials from '../components/landing/Testimonials';
import Footer from '../components/landing/Footer';

const LandingPage = () => {
  return (
    <div className="min-h-screen">
      <div className="h-screen bg-gradient-to-r from-blue-800 to-blue-900 relative overflow-hidden">
        <Navbar />
        <Hero />
        
        {/* Background elements */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-[-1]">
          <div className="absolute top-0 right-0 w-1/3 h-1/3 bg-blue-400 rounded-full filter blur-3xl opacity-20 transform translate-x-1/2 -translate-y-1/2"></div>
          <div className="absolute bottom-0 left-0 w-1/2 h-1/2 bg-teal-400 rounded-full filter blur-3xl opacity-10 transform -translate-x-1/3 translate-y-1/3"></div>
        </div>
      </div>
      
      <Features />
      <Testimonials />
      <Footer />
    </div>
  );
};

export default LandingPage;