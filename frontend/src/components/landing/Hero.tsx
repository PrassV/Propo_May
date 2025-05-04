import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, CheckCircle, Building2 } from 'lucide-react';
import Button from '../ui/Button';

const Hero = () => {
  return (
    <div className="relative overflow-hidden bg-white">
      <div className="mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:px-8">
        <div className="flex flex-col lg:flex-row items-center gap-10">
          <motion.div 
            className="max-w-2xl"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
              Simplify Your Property Management
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Propo streamlines property management with intuitive tools for owners and tenants. 
              Track rent payments, maintenance requests, and property details all in one place.
            </p>
            <div className="mt-10 flex items-center gap-x-6">
              <Button size="lg" className="px-8 py-3.5 rounded-xl">
                Get Started <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Button variant="outline" size="lg" className="px-8 py-3.5 rounded-xl">
                Learn More
              </Button>
            </div>
            
            <div className="mt-12 grid grid-cols-1 sm:grid-cols-2 gap-4">
              {[
                'Streamlined rent collection',
                'Maintenance tracking',
                'Financial reporting',
                'Tenant communication',
              ].map((feature, index) => (
                <motion.div 
                  key={index} 
                  className="flex items-center gap-2"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.5 + index * 0.1 }}
                >
                  <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
                  <span className="text-gray-600">{feature}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
          
          <motion.div 
            className="flex-1 flex justify-center"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="relative w-full max-w-md">
              <div className="absolute -inset-1 rounded-xl bg-gradient-to-r from-blue-600 to-teal-500 opacity-30 blur-xl"></div>
              <div className="relative bg-white rounded-xl shadow-xl overflow-hidden border border-gray-200">
                <div className="p-6 bg-blue-700 text-white flex items-center">
                  <Building2 className="h-8 w-8 mr-3" />
                  <h2 className="text-xl font-semibold">Property Dashboard</h2>
                </div>
                <div className="p-6">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                      <span className="font-medium">Total Properties</span>
                      <span className="text-xl font-bold text-blue-700">12</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                      <span className="font-medium">Occupancy Rate</span>
                      <span className="text-xl font-bold text-green-600">94%</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
                      <span className="font-medium">Monthly Revenue</span>
                      <span className="text-xl font-bold text-yellow-600">$24,500</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Hero;