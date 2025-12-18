import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Activity, AlertTriangle, CheckCircle, Clock, TrendingUp, RefreshCw } from 'lucide-react';
import { dashboard } from '../api';

interface DashboardStats {
    total_error_groups: number;
    pending_proposals: number;
    applied_fixes: number;
    active_rules: number;
}

const Dashboard: React.FC = () => {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    useEffect(() => {
        loadStats();
    }, []);

    const loadStats = async () => {
        try {
            setRefreshing(true);
            const response = await dashboard.getStats();
            setStats(response.data);
        } catch (error) {
            console.error('Failed to load stats:', error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-cyan-500 border-t-transparent"></div>
                    <p className="text-gray-400 mt-4">Loading dashboard...</p>
                </div>
            </div>
        );
    }

    const chartData = [
        { name: 'Error Groups', value: stats?.total_error_groups || 0, color: '#ef4444' },
        { name: 'Pending', value: stats?.pending_proposals || 0, color: '#f59e0b' },
        { name: 'Applied', value: stats?.applied_fixes || 0, color: '#10b981' },
        { name: 'Active Rules', value: stats?.active_rules || 0, color: '#06b6d4' },
    ];

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-cyan-100 to-blue-200 bg-clip-text text-transparent mb-2">
                        Dashboard
                    </h1>
                    <p className="text-gray-400">Monitor your log parsing health in real-time</p>
                </div>
                <button
                    onClick={loadStats}
                    disabled={refreshing}
                    className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-xl hover:from-cyan-600 hover:to-blue-700 transition-all shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/40 disabled:opacity-50 disabled:cursor-not-allowed group"
                >
                    <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : 'group-hover:rotate-180 transition-transform duration-500'}`} />
                    <span className="font-medium">Refresh</span>
                </button>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    icon={<AlertTriangle className="w-8 h-8" />}
                    title="Error Groups"
                    value={stats?.total_error_groups || 0}
                    trend="+12%"
                    trendUp={false}
                    gradient="from-red-500 to-orange-500"
                    bgGradient="from-red-500/10 to-orange-500/10"
                />
                <StatCard
                    icon={<Clock className="w-8 h-8" />}
                    title="Pending Proposals"
                    value={stats?.pending_proposals || 0}
                    trend="+5%"
                    trendUp={true}
                    gradient="from-yellow-500 to-orange-500"
                    bgGradient="from-yellow-500/10 to-orange-500/10"
                />
                <StatCard
                    icon={<CheckCircle className="w-8 h-8" />}
                    title="Applied Fixes"
                    value={stats?.applied_fixes || 0}
                    trend="+23%"
                    trendUp={true}
                    gradient="from-green-500 to-emerald-500"
                    bgGradient="from-green-500/10 to-emerald-500/10"
                />
                <StatCard
                    icon={<Activity className="w-8 h-8" />}
                    title="Active Rules"
                    value={stats?.active_rules || 0}
                    trend="+8%"
                    trendUp={true}
                    gradient="from-cyan-500 to-blue-500"
                    bgGradient="from-cyan-500/10 to-blue-500/10"
                />
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Bar Chart */}
                <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-slate-700/50 hover:border-cyan-500/30 transition-all">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-xl font-semibold text-white">System Overview</h2>
                        <div className="px-3 py-1 bg-cyan-500/10 text-cyan-400 text-xs font-medium rounded-full border border-cyan-500/20">
                            Live Data
                        </div>
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={chartData}>
                            <defs>
                                <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.8} />
                                    <stop offset="100%" stopColor="#0284c7" stopOpacity={0.3} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
                            <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
                            <YAxis stroke="#94a3b8" fontSize={12} />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#1e293b',
                                    border: '1px solid #334155',
                                    borderRadius: '0.75rem',
                                    boxShadow: '0 10px 30px rgba(0,0,0,0.3)',
                                }}
                                labelStyle={{ color: '#f1f5f9' }}
                            />
                            <Bar dataKey="value" fill="url(#barGradient)" radius={[8, 8, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {/* Activity Chart */}
                <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-slate-700/50 hover:border-cyan-500/30 transition-all">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-xl font-semibold text-white">Activity Trend</h2>
                        <div className="flex items-center space-x-2 text-green-400 text-sm">
                            <TrendingUp className="w-4 h-4" />
                            <span className="font-medium">+15.3%</span>
                        </div>
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={chartData}>
                            <defs>
                                <linearGradient id="lineGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.8} />
                                    <stop offset="100%" stopColor="#0284c7" stopOpacity={0.1} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
                            <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
                            <YAxis stroke="#94a3b8" fontSize={12} />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#1e293b',
                                    border: '1px solid #334155',
                                    borderRadius: '0.75rem',
                                    boxShadow: '0 10px 30px rgba(0,0,0,0.3)',
                                }}
                                labelStyle={{ color: '#f1f5f9' }}
                            />
                            <Line
                                type="monotone"
                                dataKey="value"
                                stroke="#06b6d4"
                                strokeWidth={3}
                                fill="url(#lineGradient)"
                                dot={{ fill: '#06b6d4', strokeWidth: 2, r: 5 }}
                                activeDot={{ r: 7, fill: '#0284c7' }}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

interface StatCardProps {
    icon: React.ReactNode;
    title: string;
    value: number;
    trend: string;
    trendUp: boolean;
    gradient: string;
    bgGradient: string;
}

const StatCard: React.FC<StatCardProps> = ({ icon, title, value, trend, trendUp, gradient, bgGradient }) => {
    return (
        <div className="group relative bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-slate-700/50 hover:border-cyan-500/30 transition-all hover:shadow-2xl hover:shadow-cyan-500/10 hover:-translate-y-1">
            {/* Gradient overlay on hover */}
            <div className={`absolute inset-0 bg-gradient-to-br ${bgGradient} opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl`}></div>

            <div className="relative">
                <div className="flex items-start justify-between mb-4">
                    <div className={`p-3 bg-gradient-to-br ${gradient} rounded-xl shadow-lg`}>
                        <div className="text-white">{icon}</div>
                    </div>
                    <div className={`flex items-center space-x-1 text-xs font-medium px-2 py-1 rounded-full ${trendUp ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
                        }`}>
                        <TrendingUp className={`w-3 h-3 ${!trendUp && 'rotate-180'}`} />
                        <span>{trend}</span>
                    </div>
                </div>
                <div>
                    <p className="text-gray-400 text-sm font-medium mb-1">{title}</p>
                    <p className="text-4xl font-bold text-white tracking-tight">{value.toLocaleString()}</p>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
