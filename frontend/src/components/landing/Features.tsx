import React from 'react';
import { motion } from 'framer-motion';
import { 
  BuildingIcon, 
  UserCheck, 
  CreditCard, 
  BarChart4, 
  FileText, 
  MessageSquare 
} from 'lucide-react';

const features = [
  {
    name: 'Property Management',
    description: 'Track all property details, unit information, and maintenance history in one place.',
    icon: BuildingIcon,
  },
  {
    name: 'Tenant Screening',
    description: 'Streamline applicant verification with background and credit checks for potential tenants.',
    icon: UserCheck,
  },
  {
    name: 'Rent Collection',
    description: 'Automate rent collection, late fees, and payment reminders to improve cash flow.',
    icon: CreditCard,
  },
  {
    name: 'Financial Reporting',
    description: 'Generate detailed financial reports, income statements, and tax documents.',
    icon: BarChart4,
  },
  {
    name: 'Lease Management',
    description: 'Create, manage, and renew leases with digital signatures and automated reminders.',
    icon: FileText,
  },
  {
    name: 'Communication Tools',
    description: 'Keep in touch with tenants through integrated messaging and announcement systems.',
    icon: MessageSquare,
  },
];

const Features = () => {
  return (
    <div className="py-24 bg-gray-50 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-base font-semibold leading-7 text-blue-600">Comprehensive Management</h2>
          <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Everything you need to manage properties
          </p>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            Our platform streamlines every aspect of property management so you can focus on growing your business.
          </p>
        </div>
        
        <div className="mt-20 max-w-lg sm:mx-auto md:max-w-none">
          <div className="grid grid-cols-1 gap-y-16 md:grid-cols-2 lg:grid-cols-3 md:gap-x-8 md:gap-y-12">
            {features.map((feature, index) => (
              <motion.div
                key={feature.name}
                className="relative bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-all"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true, margin: '-100px' }}
              >
                <div className="absolute top-0 -translate-y-1/2 left-6 w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                  <feature.icon className="h-6 w-6 text-blue-700" aria-hidden="true" />
                </div>
                <h3 className="mt-3 text-lg font-semibold leading-8 text-gray-900">{feature.name}</h3>
                <p className="mt-2 text-base leading-7 text-gray-600">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Features;