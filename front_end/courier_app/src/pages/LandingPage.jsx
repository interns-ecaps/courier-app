// src/pages/LandingPage.jsx
import React from 'react';

const LandingPage = () => (
  <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
    {/* Navbar */}
    <header className="w-full py-6 px-8 flex justify-end items-center bg-white shadow-md sticky top-0 z-10">
      <nav className="space-x-6">
        <a href="/Signup" className="text-gray-700 hover:text-orange-600 font-medium">Sign Up</a>
        <a href="/Login" className="bg-orange-500 text-white px-4 py-2 rounded hover:bg-orange-600 font-medium transition">Login</a>
      </nav>
    </header>

    {/* Hero */}
    <section className="w-full py-20 px-4 sm:px-8 flex-1">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-10 items-center">
          <div className="space-y-6">
            <h1 className="text-4xl md:text-5xl font-bold leading-tight">
              Efficient Shipment, Delivered
            </h1>
            <p className="text-lg text-gray-600">
              Our platform streamlines shipments with real‑time tracking, automated logistics, and transparent pricing—designed to keep your goods moving.
            </p>
            <div className="space-x-4">
              <a href="/Signup" className="inline-block bg-orange-500 text-white px-6 py-3 rounded hover:bg-orange-600 font-medium transition">
                Sign Up
              </a>
              <a href="/Login" className="inline-block border border-orange-500 text-orange-500 px-6 py-3 rounded hover:bg-orange-100 font-medium transition">
                Login
              </a>
            </div>
          </div>
          <div className="flex justify-center">
            <img 
              src="/assets/images/hero-shipment.png" 
              alt="Shipment illustration" 
              className="w-full max-w-md rounded-lg shadow-md"
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />
          </div>
        </div>
      </div>
    </section>

    {/* Services */}
    <section className="bg-white py-16">
      <div className="container mx-auto px-8">
        <h2 className="text-3xl font-semibold text-center mb-12">Our Services</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {[
            { title: 'Real-Time Tracking', desc: 'Monitor shipments live.', icon: '🚚' },
            { title: 'Route Optimization', desc: 'Fastest path planning.', icon: '🛣️' },
            { title: 'Insurance Included', desc: 'Ship with confidence.', icon: '🛡️' },
          ].map((service) => (
            <div key={service.title} className="p-6 border rounded-lg text-center hover:shadow-lg transition">
              <div className="text-4xl mb-4">{service.icon}</div>
              <h3 className="text-xl font-medium mb-2">{service.title}</h3>
              <p className="text-gray-600">{service.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>

    {/* Footer with Contact Form */}
    <footer className="bg-gray-800 text-white py-16">
      <div className="container mx-auto px-8 text-center">
        <h3 className="text-2xl font-semibold mb-4">Get In Touch</h3>
        <p className="mb-8">Fill out the form and our team will reach out to you shortly.</p>
        <form className="max-w-lg mx-auto space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <input 
              type="text" 
              placeholder="Your Name" 
              className="p-3 rounded bg-gray-700 placeholder-gray-400 text-white border border-gray-600 focus:border-orange-500 focus:outline-none" 
            />
            <input 
              type="email" 
              placeholder="Email Address" 
              className="p-3 rounded bg-gray-700 placeholder-gray-400 text-white border border-gray-600 focus:border-orange-500 focus:outline-none" 
            />
          </div>
          <textarea 
            placeholder="Your Message" 
            className="w-full p-3 rounded bg-gray-700 placeholder-gray-400 text-white h-32 border border-gray-600 focus:border-orange-500 focus:outline-none"
          ></textarea>
          <button 
            type="submit" 
            className="w-full bg-orange-500 hover:bg-orange-600 transition rounded py-3 font-medium"
          >
            Send Message
          </button>
        </form>
      </div>
    </footer>
  </div>
);

export default LandingPage;