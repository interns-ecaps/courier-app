import React from 'react';

const LandingPage = () => (
  <div className="max-h-screen flex flex-col bg-gray-50 text-gray-800">
    {/* Navbar */}
    <header className="w-full py-6 px-8 flex justify-end items-center bg-white shadow-md sticky top-0 z-10">
      <nav className="space-x-6">
        <a href="#" className="text-gray-700 hover:text-orange-600 font-medium">Sign Up</a>
        <a href="#" className="bg-orange-500 text-white px-4 py-2 rounded hover:bg-orange-600 font-medium transition">Login</a>
      </nav>
    </header>

    {/* Hero */}
    <section className="w-full py-20 px-4 sm:px-8">
      <div className="flex flex-col-reverse md:flex-row justify-between items-center max-w-7xl mx-auto gap-10">
        <h1 className="text-4xl md:text-5xl font-bold">Efficient Shipment, Delivered</h1>
        <p className="text-lg text-gray-600">
          Our platform streamlines shipments with real‑time tracking, automated logistics, and transparent pricing—designed to keep your goods moving.
        </p>
        <div className="space-x-4">
          <a href="#" className="inline-block bg-orange-500 text-white px-6 py-3 rounded hover:bg-orange-600 font-medium transition">
            Sign Up
          </a>
          <a href="#" className="inline-block border border-orange-500 text-orange-500 px-6 py-3 rounded hover:bg-orange-100 font-medium transition">
            Login
          </a>
        </div>
      </div>
      <div className="md:w-1/2">
        <img src="/assets/images/hero-shipment.png" alt="Shipment illustration" className="w-full rounded-lg shadow-md" />
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
          ].map((s) => (
            <div key={s.title} className="p-6 border rounded-lg text-center hover:shadow-lg transition">
              <div className="text-4xl mb-4">{s.icon}</div>
              <h3 className="text-xl font-medium mb-2">{s.title}</h3>
              <p className="text-gray-600">{s.desc}</p>
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
        <form className="max-w-lg mx-auto grid grid-cols-1 sm:grid-cols-2 gap-4">
          <input type="text" placeholder="Your Name" className="p-3 rounded bg-gray-700 placeholder-gray-400 text-white" />
          <input type="email" placeholder="Email Address" className="p-3 rounded bg-gray-700 placeholder-gray-400 text-white" />
          <textarea placeholder="Your Message" className="sm:col-span-2 p-3 rounded bg-gray-700 placeholder-gray-400 text-white h-32"></textarea>
          <button type="submit" className="sm:col-span-2 bg-orange-500 hover:bg-orange-600 transition rounded py-3 font-medium">Send Message</button>
        </form>
      </div>
    </footer>
  </div>
);

export default LandingPage;
