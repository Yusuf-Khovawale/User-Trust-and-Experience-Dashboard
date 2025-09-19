import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
  LineChart, Line, PieChart, Pie, Cell, ResponsiveContainer,
  AreaChart, Area
} from 'recharts';
import { 
  TrendingUp, TrendingDown, Users, ShoppingCart, 
  AlertTriangle, Shield, RefreshCw, Download,
  Filter, Calendar, Target, Award
} from 'lucide-react';
import axios from 'axios';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Color scheme
const COLORS = {
  primary: '#3B82F6',
  secondary: '#10B981', 
  warning: '#F59E0B',
  danger: '#EF4444',
  info: '#6366F1',
  success: '#059669'
};

const CHART_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#6366F1', '#8B5CF6', '#EC4899', '#14B8A6'];

// Utility Functions
const formatNumber = (num) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num.toString();
};

const formatPercentage = (num) => `${num.toFixed(1)}%`;

const formatCurrency = (num) => `$${num.toLocaleString()}`;

// Loading Component
const LoadingSpinner = () => (
  <div className="flex items-center justify-center p-8">
    <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
    <span className="ml-2 text-gray-600">Loading...</span>
  </div>
);

// Error Component
const ErrorMessage = ({ message }) => (
  <div className="bg-red-50 border border-red-200 rounded-lg p-4 m-4">
    <div className="flex items-center">
      <AlertTriangle className="h-5 w-5 text-red-500 mr-2" />
      <span className="text-red-700">{message}</span>
    </div>
  </div>
);

// KPI Card Component
const KPICard = ({ title, value, change, icon: Icon, color = "blue", suffix = "" }) => {
  const isPositive = change >= 0;
  
  return (
    <div className="bg-white rounded-lg shadow-md p-6 border-l-4" style={{ borderLeftColor: COLORS[color] }}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm font-medium">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">
            {typeof value === 'number' ? value.toFixed(1) : value}{suffix}
          </p>
          {change !== undefined && (
            <div className={`flex items-center mt-2 text-sm ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {isPositive ? <TrendingUp className="h-4 w-4 mr-1" /> : <TrendingDown className="h-4 w-4 mr-1" />}
              <span>{Math.abs(change).toFixed(1)}% from last month</span>
            </div>
          )}
        </div>
        <div className={`p-3 rounded-full`} style={{ backgroundColor: `${COLORS[color]}20` }}>
          <Icon className="h-8 w-8" style={{ color: COLORS[color] }} />
        </div>
      </div>
    </div>
  );
};

// Trust Metrics Dashboard
const TrustMetricsDashboard = () => {
  const { data: dashboardData, isLoading, error } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await axios.get(`${API}/dashboard-stats`);
      return response.data;
    }
  });

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message="Failed to load dashboard data" />;

  const { trust_metrics, totals, recent_activity } = dashboardData;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <KPICard
        title="Trust Index"
        value={trust_metrics.trust_index}
        change={2.3}
        icon={Shield}
        color="primary"
        suffix="/100"
      />
      <KPICard
        title="Dispute Rate"
        value={trust_metrics.dispute_rate}
        change={-0.8}
        icon={AlertTriangle}
        color="warning"
        suffix="%"
      />
      <KPICard
        title="User Satisfaction"
        value={trust_metrics.user_satisfaction_avg}
        change={1.2}
        icon={Award}
        color="success"
        suffix="%"
      />
      <KPICard
        title="Repeat Purchase Rate"
        value={trust_metrics.repeat_purchase_uplift}
        change={3.1}
        icon={Target}
        color="info"
        suffix="%"
      />
    </div>
  );
};

// Category Performance Chart
const CategoryPerformanceChart = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['category-analysis'],
    queryFn: async () => {
      const response = await axios.get(`${API}/category-analysis`);
      return response.data.categories;
    }
  });

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message="Failed to load category data" />;

  const chartData = data.map(cat => ({
    category: cat._id,
    trustIndex: cat.avg_trust_index,
    fulfillmentRate: cat.avg_fulfillment_rate * 100,
    disputeRate: cat.avg_dispute_rate * 100,
    sellers: cat.total_sellers
  }));

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Category Performance Analysis</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="category" angle={-45} textAnchor="end" height={80} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="trustIndex" fill={COLORS.primary} name="Trust Index" />
          <Bar dataKey="fulfillmentRate" fill={COLORS.secondary} name="Fulfillment Rate %" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

// Regional Analysis Chart
const RegionalAnalysisChart = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['regional-analysis'],
    queryFn: async () => {
      const response = await axios.get(`${API}/regional-analysis`);
      return response.data.regions;
    }
  });

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message="Failed to load regional data" />;

  const chartData = data.map(region => ({
    region: region._id,
    satisfaction: region.avg_satisfaction,
    users: region.total_users,
    avgOrders: region.avg_orders
  }));

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Regional User Satisfaction</h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="region" />
          <YAxis />
          <Tooltip />
          <Area type="monotone" dataKey="satisfaction" stroke={COLORS.info} fill={COLORS.info} fillOpacity={0.6} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

// Seller Performance Table
const SellerPerformanceTable = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['sellers-performance'],
    queryFn: async () => {
      const response = await axios.get(`${API}/sellers-performance?limit=10`);
      return response.data.sellers;
    }
  });

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message="Failed to load seller data" />;

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Performing Sellers</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Seller
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Trust Index
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Fulfillment Rate
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Complaint Ratio
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Category
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((seller) => (
              <tr key={seller.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{seller.name}</div>
                    <div className="text-sm text-gray-500">{seller.region}</div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    seller.trust_index >= 80 ? 'bg-green-100 text-green-800' :
                    seller.trust_index >= 60 ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {seller.trust_index.toFixed(1)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatPercentage(seller.fulfillment_rate * 100)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatPercentage(seller.complaint_ratio * 100)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {seller.category}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Policy Simulation Component
const PolicySimulation = () => {
  const [policyParams, setPolicyParams] = useState({
    min_fulfillment_rate: 0.9,
    max_complaint_ratio: 0.1,
    min_trust_index: 70
  });
  
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['policy-simulation', policyParams],
    queryFn: async () => {
      const params = new URLSearchParams(policyParams).toString();
      const response = await axios.get(`${API}/policy-simulation?${params}`);
      return response.data;
    }
  });

  const handleParamChange = (param, value) => {
    setPolicyParams(prev => ({ ...prev, [param]: parseFloat(value) }));
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Policy Impact Simulation</h3>
      
      {/* Policy Controls */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Min Fulfillment Rate
          </label>
          <input
            type="range"
            min="0.5"
            max="1.0"
            step="0.05"
            value={policyParams.min_fulfillment_rate}
            onChange={(e) => handleParamChange('min_fulfillment_rate', e.target.value)}
            className="w-full"
          />
          <span className="text-sm text-gray-500">
            {formatPercentage(policyParams.min_fulfillment_rate * 100)}
          </span>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Max Complaint Ratio
          </label>
          <input
            type="range"
            min="0.0"
            max="0.3"
            step="0.01"
            value={policyParams.max_complaint_ratio}
            onChange={(e) => handleParamChange('max_complaint_ratio', e.target.value)}
            className="w-full"
          />
          <span className="text-sm text-gray-500">
            {formatPercentage(policyParams.max_complaint_ratio * 100)}
          </span>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Min Trust Index
          </label>
          <input
            type="range"
            min="30"
            max="90"
            step="5"
            value={policyParams.min_trust_index}
            onChange={(e) => handleParamChange('min_trust_index', e.target.value)}
            className="w-full"
          />
          <span className="text-sm text-gray-500">
            {policyParams.min_trust_index}
          </span>
        </div>
      </div>

      {/* Simulation Results */}
      {isLoading ? (
        <LoadingSpinner />
      ) : data ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-md font-medium text-gray-900 mb-3">Impact Analysis</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Compliant Sellers:</span>
                <span className="font-medium">{data.impact_analysis.compliant_sellers}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Non-Compliant:</span>
                <span className="font-medium text-red-600">{data.impact_analysis.non_compliant_sellers}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Compliance Rate:</span>
                <span className="font-medium">{data.impact_analysis.compliance_rate}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Orders at Risk:</span>
                <span className="font-medium text-yellow-600">{formatNumber(data.impact_analysis.orders_at_risk)}</span>
              </div>
            </div>
          </div>
          
          <div className="bg-blue-50 rounded-lg p-4">
            <h4 className="text-md font-medium text-gray-900 mb-3">Recommendations</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Action:</span>
                <span className={`font-medium ${
                  data.recommendations.action === 'stricter_onboarding' ? 'text-orange-600' : 'text-green-600'
                }`}>
                  {data.recommendations.action.replace('_', ' ').toUpperCase()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Est. Trust Improvement:</span>
                <span className="font-medium text-green-600">
                  +{data.recommendations.estimated_trust_improvement.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};

// Data Generator Component
const DataGenerator = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationParams, setGenerationParams] = useState({
    num_users: 1000,
    num_sellers: 200,
    num_orders: 5000,
    num_reviews: 3000,
    num_disputes: 250,
    seed: 42
  });

  const generateData = async () => {
    setIsGenerating(true);
    try {
      await axios.post(`${API}/generate-data`, generationParams);
      // Refresh all queries
      queryClient.invalidateQueries();
      alert('Sample data generated successfully!');
    } catch (error) {
      alert('Error generating data: ' + error.message);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Generator</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Users</label>
          <input
            type="number"
            value={generationParams.num_users}
            onChange={(e) => setGenerationParams(prev => ({ ...prev, num_users: parseInt(e.target.value) }))}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Sellers</label>
          <input
            type="number"
            value={generationParams.num_sellers}
            onChange={(e) => setGenerationParams(prev => ({ ...prev, num_sellers: parseInt(e.target.value) }))}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Orders</label>
          <input
            type="number"
            value={generationParams.num_orders}
            onChange={(e) => setGenerationParams(prev => ({ ...prev, num_orders: parseInt(e.target.value) }))}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
      </div>
      <button
        onClick={generateData}
        disabled={isGenerating}
        className="bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white px-6 py-2 rounded-lg font-medium flex items-center"
      >
        {isGenerating ? (
          <>
            <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            Generating...
          </>
        ) : (
          <>
            <RefreshCw className="h-4 w-4 mr-2" />
            Generate Sample Data
          </>
        )}
      </button>
    </div>
  );
};

// Main Dashboard Component
const Dashboard = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-blue-500 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">User Trust & Experience Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button className="flex items-center px-4 py-2 text-sm text-gray-600 hover:text-gray-900">
                <Download className="h-4 w-4 mr-1" />
                Export Report
              </button>
              <button className="flex items-center px-4 py-2 text-sm text-gray-600 hover:text-gray-900">
                <Calendar className="h-4 w-4 mr-1" />
                Last 30 Days
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Data Generator */}
        <DataGenerator />
        
        {/* Trust Metrics KPIs */}
        <TrustMetricsDashboard />
        
        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <CategoryPerformanceChart />
          <RegionalAnalysisChart />
        </div>
        
        {/* Seller Performance Table */}
        <div className="mb-8">
          <SellerPerformanceTable />
        </div>
        
        {/* Policy Simulation */}
        <PolicySimulation />
      </main>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="App">
        <Dashboard />
      </div>
    </QueryClientProvider>
  );
}

export default App;