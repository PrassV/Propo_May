import React from 'react';
import { motion } from 'framer-motion';
import { Star } from 'lucide-react';

const testimonials = [
  {
    content: "PropManage has completely transformed how I handle my rental properties. The automated rent collection alone has saved me countless hours.",
    author: "Sarah Johnson",
    role: "Property Owner",
    avatarUrl: "https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg?auto=compress&cs=tinysrgb&w=120"
  },
  {
    content: "As a tenant, I love how easy it is to submit maintenance requests and pay rent. The portal makes communication with my landlord so much simpler.",
    author: "Michael Chen",
    role: "Tenant",
    avatarUrl: "https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg?auto=compress&cs=tinysrgb&w=120"
  },
  {
    content: "Managing 15 properties used to be a full-time job. With PropManage, I've cut my administrative work by 70% and can focus on growing my portfolio.",
    author: "David Rodriguez",
    role: "Property Manager",
    avatarUrl: "https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&cs=tinysrgb&w=120"
  }
];

const Testimonials = () => {
  return (
    <section className="py-24 bg-white sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Trusted by property owners and tenants
          </h2>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            Here's what our customers have to say about their experience with PropManage.
          </p>
        </div>
        
        <div className="mx-auto mt-16 grid max-w-2xl grid-cols-1 gap-8 lg:mx-0 lg:max-w-none lg:grid-cols-3">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              className="flex flex-col justify-between rounded-2xl bg-gray-50 p-8 shadow-sm ring-1 ring-gray-200"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true, margin: '-100px' }}
            >
              <div>
                <div className="flex gap-0.5 text-yellow-400">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 fill-current" />
                  ))}
                </div>
                <p className="mt-4 text-lg font-medium leading-6 text-gray-900">
                  "{testimonial.content}"
                </p>
              </div>
              <div className="mt-8 flex items-center gap-x-4">
                <img
                  className="h-12 w-12 rounded-full bg-gray-50 object-cover"
                  src={testimonial.avatarUrl}
                  alt={testimonial.author}
                />
                <div>
                  <h3 className="text-base font-semibold leading-6 text-gray-900">{testimonial.author}</h3>
                  <p className="text-sm text-gray-600">{testimonial.role}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Testimonials;