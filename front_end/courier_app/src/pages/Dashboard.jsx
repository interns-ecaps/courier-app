// import React, { useState } from 'react';
// import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
// import { Package, Truck, Users, DollarSign, Globe, Settings, Bell, Search, Menu, X, TrendingUp, AlertTriangle, CheckCircle, Clock } from 'lucide-react';

// const Dashboard = () => {
//   const [userType, setUserType] = useState('super_admin');
//   const [sidebarOpen, setSidebarOpen] = useState(false);

//   // Sample data for charts
//   const shipmentData = [
//     { month: 'Jan', shipments: 120, revenue: 45000 },
//     { month: 'Feb', shipments: 135, revenue: 52000 },
//     { month: 'Mar', shipments: 150, revenue: 58000 },
//     { month: 'Apr', shipments: 140, revenue: 55000 },
//     { month: 'May', shipments: 180, revenue: 68000 },
//     { month: 'Jun', shipments: 200, revenue: 78000 }
//   ];

//   const statusData = [
//     { name: 'Delivered', value: 65, color: '#10B981' },
//     { name: 'In Transit', value: 25, color: '#F59E0B' },
//     { name: 'Pending', value: 10, color: '#EF4444' }
//   ];

//   // Role-based configurations
//   const roleConfigs = {
//     super_admin: {
//       title: 'Super Admin Dashboard',
//       metrics: [
//         { label: 'Total Users', value: '2,847', icon: Users, color: 'text-blue-600', bg: 'bg-blue-50' },
//         { label: 'Active Shipments', value: '1,249', icon: Truck, color: 'text-orange-600', bg: 'bg-orange-50' },
//         { label: 'Total Revenue', value: '$78,340', icon: DollarSign, color: 'text-green-600', bg: 'bg-green-50' },
//         { label: 'Global Reach', value: '45 Countries', icon: Globe, color: 'text-purple-600', bg: 'bg-purple-50' }
//       ],
//       navigation: [
//         { label: 'Overview', icon: BarChart, active: true },
//         { label: 'User Management', icon: Users },
//         { label: 'System Settings', icon: Settings },
//         { label: 'Analytics', icon: TrendingUp },
//         { label: 'Notifications', icon: Bell }
//       ],
//       widgets: ['metrics', 'shipmentChart', 'statusChart', 'recentActivity']
//     },
//     importer_exporter: {
//       title: 'Importer/Exporter Dashboard',
//       metrics: [
//         { label: 'Active Shipments', value: '23', icon: Package, color: 'text-orange-600', bg: 'bg-orange-50' },
//         { label: 'Pending Customs', value: '7', icon: AlertTriangle, color: 'text-yellow-600', bg: 'bg-yellow-50' },
//         { label: 'This Month Cost', value: '$12,450', icon: DollarSign, color: 'text-green-600', bg: 'bg-green-50' },
//         { label: 'Delivered', value: '156', icon: CheckCircle, color: 'text-blue-600', bg: 'bg-blue-50' }
//       ],
//       navigation: [
//         { label: 'My Shipments', icon: Package, active: true },
//         { label: 'Tracking', icon: Truck },
//         { label: 'Documentation', icon: Settings },
//         { label: 'Reports', icon: BarChart },
//         { label: 'Support', icon: Bell }
//       ],
//       widgets: ['metrics', 'shipmentChart', 'statusChart', 'recentShipments']
//     },
//     supplier: {
//       title: 'Supplier Dashboard',
//       metrics: [
//         { label: 'Orders to Ship', value: '45', icon: Package, color: 'text-orange-600', bg: 'bg-orange-50' },
//         { label: 'In Transit', value: '12', icon: Truck, color: 'text-blue-600', bg: 'bg-blue-50' },
//         { label: 'Monthly Revenue', value: '$8,230', icon: DollarSign, color: 'text-green-600', bg: 'bg-green-50' },
//         { label: 'Avg Delivery Time', value: '4.2 days', icon: Clock, color: 'text-purple-600', bg: 'bg-purple-50' }
//       ],
//       navigation: [
//         { label: 'Orders', icon: Package, active: true },
//         { label: 'Inventory', icon: BarChart },
//         { label: 'Shipping', icon: Truck },
//         { label: 'Analytics', icon: TrendingUp },
//         { label: 'Settings', icon: Settings }
//       ],
//       widgets: ['metrics', 'orderChart', 'statusChart', 'recentOrders']
//     }
//   };

//   const currentConfig = roleConfigs[userType];

//   const MetricsWidget = () => (
//     <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mb-6 lg:mb-8">
//       {currentConfig.metrics.map((metric, index) => (
//         <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-100 p-4 lg:p-6 hover:shadow-md transition-shadow duration-200">
//           <div className="flex items-center justify-between">
//             <div className="flex-1 min-w-0">
//               <p className="text-sm font-medium text-gray-600 truncate">{metric.label}</p>
//               <p className="text-xl lg:text-2xl font-bold text-gray-900 mt-1">{metric.value}</p>
//             </div>
//             <div className={`p-2 lg:p-3 rounded-full ${metric.bg} flex-shrink-0 ml-3`}>
//               <metric.icon className={`h-5 w-5 lg:h-6 lg:w-6 ${metric.color}`} />
//             </div>
//           </div>
//         </div>
//       ))}
//     </div>
//   );

//   const ShipmentChart = () => (
//     <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-4 lg:p-6 mb-6">
//       <h3 className="text-lg font-semibold text-gray-900 mb-4">Shipment Trends</h3>
//       <div className="h-64 lg:h-80">
//         <ResponsiveContainer width="100%" height="100%">
//           <LineChart data={shipmentData}>
//             <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
//             <XAxis dataKey="month" stroke="#6b7280" fontSize={12} />
//             <YAxis stroke="#6b7280" fontSize={12} />
//             <Tooltip 
//               contentStyle={{
//                 backgroundColor: 'white',
//                 border: '1px solid #e5e7eb',
//                 borderRadius: '8px',
//                 boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
//               }}
//             />
//             <Line 
//               type="monotone" 
//               dataKey="shipments" 
//               stroke="#f97316" 
//               strokeWidth={3}
//               dot={{ fill: '#f97316', strokeWidth: 2, r: 4 }}
//               activeDot={{ r: 6, stroke: '#f97316', strokeWidth: 2 }}
//             />
//           </LineChart>
//         </ResponsiveContainer>
//       </div>
//     </div>
//   );

//   const StatusChart = () => (
//     <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-4 lg:p-6 mb-6">
//       <h3 className="text-lg font-semibold text-gray-900 mb-4">Shipment Status</h3>
//       <div className="h-64 lg:h-80">
//         <ResponsiveContainer width="100%" height="100%">
//           <PieChart>
//             <Pie
//               data={statusData}
//               cx="50%"
//               cy="50%"
//               labelLine={false}
//               label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
//               outerRadius={80}
//               fill="#8884d8"
//               dataKey="value"
//             >
//               {statusData.map((entry, index) => (
//                 <Cell key={`cell-${index}`} fill={entry.color} />
//               ))}
//             </Pie>
//             <Tooltip 
//               contentStyle={{
//                 backgroundColor: 'white',
//                 border: '1px solid #e5e7eb',
//                 borderRadius: '8px',
//                 boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
//               }}
//             />
//           </PieChart>
//         </ResponsiveContainer>
//       </div>
//     </div>
//   );

//   const RecentActivity = () => (
//     <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-4 lg:p-6">
//       <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
//       <div className="space-y-3">
//         {[
//           { action: 'New user registered', time: '2 hours ago', type: 'user' },
//           { action: 'Shipment #12345 delivered', time: '4 hours ago', type: 'shipment' },
//           { action: 'System maintenance completed', time: '1 day ago', type: 'system' },
//           { action: 'Payment processed for order #67890', time: '2 days ago', type: 'payment' }
//         ].map((activity, index) => (
//           <div key={index} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors duration-150">
//             <div className="w-2 h-2 bg-orange-500 rounded-full flex-shrink-0"></div>
//             <div className="flex-1 min-w-0">
//               <p className="text-sm font-medium text-gray-900">{activity.action}</p>
//               <p className="text-xs text-gray-500 mt-0.5">{activity.time}</p>
//             </div>
//           </div>
//         ))}
//       </div>
//     </div>
//   );

//   return (
//     <div className="min-h-screen bg-gray-50">
//       {/* Mobile Sidebar Overlay */}
//       {sidebarOpen && (
//         <div className="fixed inset-0 z-40 lg:hidden">
//           <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)}></div>
//         </div>
//       )}

//       {/* Sidebar */}
//       <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg border-r border-gray-200 transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}>
//         <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
//           <h2 className="text-xl font-bold text-gray-800">ShipDash</h2>
//           <button 
//             onClick={() => setSidebarOpen(false)}
//             className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
//           >
//             <X className="h-5 w-5" />
//           </button>
//         </div>
        
//         <nav className="mt-6 px-3">
//           {currentConfig.navigation.map((item, index) => (
//             <a
//               key={index}
//               href="#"
//               className={`flex items-center px-3 py-2.5 mb-1 rounded-lg text-sm font-medium transition-colors duration-150 ${
//                 item.active 
//                   ? 'bg-orange-50 text-orange-700 border-r-2 border-orange-500' 
//                   : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
//               }`}
//             >
//               <item.icon className="h-5 w-5 mr-3 flex-shrink-0" />
//               <span className="truncate">{item.label}</span>
//             </a>
//           ))}
//         </nav>

//         {/* User Type Selector */}
//         <div className="absolute bottom-4 left-4 right-4">
//           <label className="block text-sm font-medium text-gray-700 mb-2">Switch Role:</label>
//           <select 
//             value={userType} 
//             onChange={(e) => setUserType(e.target.value)}
//             className="w-full p-2.5 border border-gray-300 rounded-lg text-sm bg-white focus:border-orange-500 focus:ring-2 focus:ring-orange-200 focus:outline-none transition-colors"
//           >
//             <option value="super_admin">Super Admin</option>
//             <option value="importer_exporter">Importer/Exporter</option>
//             <option value="supplier">Supplier</option>
//           </select>
//         </div>
//       </div>

//       {/* Main Content */}
//       <div className="lg:ml-64 flex flex-col min-h-screen">
//         {/* Header */}
//         <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-30">
//           <div className="flex items-center justify-between px-4 lg:px-6 py-4">
//             <div className="flex items-center min-w-0">
//               <button 
//                 onClick={() => setSidebarOpen(true)}
//                 className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 mr-2 transition-colors"
//               >
//                 <Menu className="h-5 w-5" />
//               </button>
//               <h1 className="text-xl lg:text-2xl font-bold text-gray-900 truncate">{currentConfig.title}</h1>
//             </div>
//             <div className="flex items-center space-x-2 lg:space-x-4">
//               <div className="relative hidden sm:block">
//                 <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
//                 <input 
//                   type="text" 
//                   placeholder="Search..." 
//                   className="pl-9 pr-4 py-2 w-40 lg:w-64 border border-gray-300 rounded-lg text-sm focus:border-orange-500 focus:ring-2 focus:ring-orange-200 focus:outline-none transition-colors"
//                 />
//               </div>
//               <button className="p-2 rounded-lg bg-orange-50 text-orange-600 hover:bg-orange-100 transition-colors duration-150">
//                 <Bell className="h-5 w-5" />
//               </button>
//               <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
//                 <span className="text-white text-sm font-medium">U</span>
//               </div>
//             </div>
//           </div>
//         </header>

//         {/* Dashboard Content */}
//         <main className="flex-1 p-4 lg:p-6">
//           <MetricsWidget />
          
//           <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 lg:gap-6 mb-6 lg:mb-8">
//             <ShipmentChart />
//             <StatusChart />
//           </div>
          
//           <RecentActivity />
//         </main>
//       </div>
//     </div>
//   );  
// }
