import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Building2, Menu, X } from 'lucide-react';
import Button from '../ui/Button';

const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 10) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header
      className={`fixed w-full z-50 transition-all duration-300 ${
        isScrolled ? 'bg-white shadow-md py-3' : 'bg-transparent py-5'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <nav className="flex items-center justify-between">
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <Building2 className={`h-8 w-8 ${isScrolled ? 'text-blue-700' : 'text-blue-500'}`} />
              <span className={`text-xl font-bold ${isScrolled ? 'text-gray-900' : 'text-white'}`}>
                PropManage
              </span>
            </Link>
            
            <div className="hidden md:flex ml-10 space-x-8">
              {['Features', 'Pricing', 'About', 'Contact'].map((item) => (
                <a
                  key={item}
                  href={`#${item.toLowerCase()}`}
                  className={`text-sm font-medium ${
                    isScrolled ? 'text-gray-700 hover:text-blue-700' : 'text-gray-200 hover:text-white'
                  } transition-colors`}
                >
                  {item}
                </a>
              ))}
            </div>
          </div>
          
          <div className="hidden md:flex items-center space-x-4">
            <Link to="/login">
              <Button variant="outline" className={isScrolled ? '' : 'border-white text-white hover:bg-white hover:text-gray-900'}>
                Sign In
              </Button>
            </Link>
            <Link to="/signup">
              <Button className={isScrolled ? '' : 'bg-white text-gray-900 hover:bg-gray-100'}>
                Sign Up
              </Button>
            </Link>
          </div>
          
          <button
            className="md:hidden"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? (
              <X className={`h-6 w-6 ${isScrolled ? 'text-gray-900' : 'text-white'}`} />
            ) : (
              <Menu className={`h-6 w-6 ${isScrolled ? 'text-gray-900' : 'text-white'}`} />
            )}
          </button>
        </nav>
      </div>
      
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            className="md:hidden bg-white"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="px-4 pt-2 pb-3 space-y-1 sm:px-6">
              {['Features', 'Pricing', 'About', 'Contact'].map((item) => (
                <a
                  key={item}
                  href={`#${item.toLowerCase()}`}
                  className="block py-2 text-base font-medium text-gray-700 hover:text-blue-700"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {item}
                </a>
              ))}
              <div className="pt-4 pb-2 border-t border-gray-200 flex flex-col space-y-2">
                <Link 
                  to="/login"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <Button variant="outline" className="w-full">
                    Sign In
                  </Button>
                </Link>
                <Link 
                  to="/signup"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <Button className="w-full">
                    Sign Up
                  </Button>
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
};

export default Navbar;