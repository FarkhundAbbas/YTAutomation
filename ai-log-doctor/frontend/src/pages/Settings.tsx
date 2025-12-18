import React, { useEffect, useState } from 'react';
import { Server, Plus, Check, X, RefreshCw } from 'lucide-react';

interface SIEMConnector {
    id: number;
    name: string;
    platform: string;
    base_url: string;
    is_active: boolean;
    last_tested?: string;
    last_test_status?: string;
}

const Settings: React.FC = () => {
    const [connectors, setConnectors] = useState<SIEMConnector[]>([]);
    const [loading, setLoading] = useState(true);
    const [showAddForm, setShowAddForm] = useState(false);
    const [newConnector, setNewConnector] = useState({
        name: '',
        platform: 'generic',
        base_url: '',
        api_key: '',
        username: '',
        password: ''
    });

    useEffect(() => {
        loadConnectors();
    }, []);

    const loadConnectors = async () => {
        try {
            // Mock data for demo - in production this would call the API
            const mockConnectors: SIEMConnector[] = [
                {
                    id: 1,
                    name: 'QRadar Production',
                    platform: 'qradar',
                    base_url: 'https://qradar.example.com',
                    is_active: true,
                    last_tested: new Date().toISOString(),
                    last_test_status: 'success'
                },
                {
                    id: 2,
                    name: 'Wazuh Manager',
                    platform: 'wazuh',
                    base_url: 'https://wazuh.example.com:55000',
                    is_active: true,
                    last_tested: new Date(Date.now() - 3600000).toISOString(),
                    last_test_status: 'success'
                },
                {
                    id: 3,
                    name: 'Splunk Enterprise',
                    platform: 'splunk',
                    base_url: 'https://splunk.example.com:8088',
                    is_active: false,
                    last_tested: new Date(Date.now() - 86400000).toISOString(),
                    last_test_status: 'failed'
                }
            ];
            setConnectors(mockConnectors);
        } catch (error) {
            console.error('Failed to load connectors:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleAddConnector = async () => {
        try {
            // In production, this would call the API
            const newConn: SIEMConnector = {
                id: connectors.length + 1,
                name: newConnector.name,
                platform: newConnector.platform,
                base_url: newConnector.base_url,
                is_active: true,
                last_tested: new Date().toISOString(),
                last_test_status: 'pending'
            };
            setConnectors([...connectors, newConn]);
            setShowAddForm(false);
            setNewConnector({
                name: '',
                platform: 'generic',
                base_url: '',
                api_key: '',
                username: '',
                password: ''
            });
        } catch (error) {
            console.error('Failed to add connector:', error);
        }
    };

    const handleTestConnection = async (connectorId: number) => {
        console.log(`Testing connector ${connectorId}`);
        // Update connector status
        setConnectors(connectors.map(c =>
            c.id === connectorId
                ? { ...c, last_tested: new Date().toISOString(), last_test_status: 'success' }
                : c
        ));
    };

    const handleToggleActive = (connectorId: number) => {
        setConnectors(connectors.map(c =>
            c.id === connectorId ? { ...c, is_active: !c.is_active } : c
        ));
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-cyan-500 border-t-transparent"></div>
                    <p className="text-gray-400 mt-4">Loading SIEM integrations...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-cyan-100 to-blue-200 bg-clip-text text-transparent mb-2">
                        SIEM Integrations
                    </h1>
                    <p className="text-gray-400">Manage connections to your SIEM platforms</p>
                </div>
                <button
                    onClick={() => setShowAddForm(true)}
                    className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-xl hover:from-cyan-600 hover:to-blue-700 transition-all shadow-lg"
                >
                    <Plus className="w-5 h-5" />
                    <span className="font-medium">Add Connector</span>
                </button>
            </div>

            {/* Add Connector Form */}
            {showAddForm && (
                <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-slate-700/50">
                    <h2 className="text-xl font-semibold text-white mb-4">Add New SIEM Connector</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="text-sm font-medium text-gray-400 mb-2 block">Name</label>
                            <input
                                type="text"
                                value={newConnector.name}
                                onChange={(e) => setNewConnector({ ...newConnector, name: e.target.value })}
                                className="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-cyan-500 focus:outline-none"
                                placeholder="Production QRadar"
                            />
                        </div>
                        <div>
                            <label className="text-sm font-medium text-gray-400 mb-2 block">Platform</label>
                            <select
                                value={newConnector.platform}
                                onChange={(e) => setNewConnector({ ...newConnector, platform: e.target.value })}
                                className="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-cyan-500 focus:outline-none"
                            >
                                <option value="generic">Generic</option>
                                <option value="qradar">IBM QRadar</option>
                                <option value="wazuh">Wazuh</option>
                                <option value="splunk">Splunk</option>
                                <option value="elastic">Elastic</option>
                            </select>
                        </div>
                        <div className="md:col-span-2">
                            <label className="text-sm font-medium text-gray-400 mb-2 block">Base URL</label>
                            <input
                                type="text"
                                value={newConnector.base_url}
                                onChange={(e) => setNewConnector({ ...newConnector, base_url: e.target.value })}
                                className="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-cyan-500 focus:outline-none"
                                placeholder="https://siem.example.com"
                            />
                        </div>
                        <div>
                            <label className="text-sm font-medium text-gray-400 mb-2 block">Username (optional)</label>
                            <input
                                type="text"
                                value={newConnector.username}
                                onChange={(e) => setNewConnector({ ...newConnector, username: e.target.value })}
                                className="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-cyan-500 focus:outline-none"
                                placeholder="admin"
                            />
                        </div>
                        <div>
                            <label className="text-sm font-medium text-gray-400 mb-2 block">Password / API Key</label>
                            <input
                                type="password"
                                value={newConnector.password}
                                onChange={(e) => setNewConnector({ ...newConnector, password: e.target.value })}
                                className="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-4 py-2 text-white focus:border-cyan-500 focus:outline-none"
                                placeholder="••••••••"
                            />
                        </div>
                    </div>
                    <div className="flex space-x-3 mt-6">
                        <button
                            onClick={handleAddConnector}
                            className="flex-1 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl hover:from-green-600 hover:to-emerald-700 transition-all"
                        >
                            Add Connector
                        </button>
                        <button
                            onClick={() => setShowAddForm(false)}
                            className="flex-1 px-6 py-3 bg-slate-700 text-white rounded-xl hover:bg-slate-600 transition-all"
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            )}

            {/* Connectors List */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {connectors.map((connector) => (
                    <ConnectorCard
                        key={connector.id}
                        connector={connector}
                        onTest={() => handleTestConnection(connector.id)}
                        onToggle={() => handleToggleActive(connector.id)}
                    />
                ))}
            </div>

            {connectors.length === 0 && !showAddForm && (
                <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-16 text-center border border-slate-700/50">
                    <Server className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                    <p className="text-gray-400 text-lg mb-2">No SIEM connectors configured</p>
                    <p className="text-gray-500 text-sm">Add your first connector to start integrating with your SIEM platform</p>
                </div>
            )}
        </div>
    );
};

interface ConnectorCardProps {
    connector: SIEMConnector;
    onTest: () => void;
    onToggle: () => void;
}

const ConnectorCard: React.FC<ConnectorCardProps> = ({ connector, onTest, onToggle }) => {
    const getPlatformColor = (platform: string) => {
        const colors: Record<string, string> = {
            qradar: 'from-blue-500 to-indigo-600',
            wazuh: 'from-green-500 to-emerald-600',
            splunk: 'from-orange-500 to-red-600',
            elastic: 'from-cyan-500 to-blue-600',
            generic: 'from-gray-500 to-slate-600'
        };
        return colors[platform] || colors.generic;
    };

    const getStatusColor = (status?: string) => {
        if (status === 'success') return 'text-green-400';
        if (status === 'failed') return 'text-red-400';
        return 'text-yellow-400';
    };

    return (
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-slate-700/50 hover:border-cyan-500/30 transition-all">
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                    <div className={`p-3 bg-gradient-to-br ${getPlatformColor(connector.platform)} rounded-xl`}>
                        <Server className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h3 className="text-white font-semibold text-lg">{connector.name}</h3>
                        <p className="text-gray-400 text-sm capitalize">{connector.platform}</p>
                    </div>
                </div>
                <button
                    onClick={onToggle}
                    className={`p-2 rounded-lg transition-all ${connector.is_active
                        ? 'bg-green-500/20 text-green-400'
                        : 'bg-gray-500/20 text-gray-400'
                        }`}
                >
                    {connector.is_active ? <Check className="w-5 h-5" /> : <X className="w-5 h-5" />}
                </button>
            </div>

            <div className="space-y-3">
                <div>
                    <p className="text-xs text-gray-400 mb-1">Base URL</p>
                    <p className="text-sm text-white font-mono bg-slate-900/50 px-3 py-2 rounded-lg">
                        {connector.base_url}
                    </p>
                </div>

                {connector.last_tested && (
                    <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-400">Last Tested:</span>
                        <span className={getStatusColor(connector.last_test_status)}>
                            {new Date(connector.last_tested).toLocaleString()}
                        </span>
                    </div>
                )}

                <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Status:</span>
                    <span className={connector.is_active ? 'text-green-400' : 'text-gray-400'}>
                        {connector.is_active ? 'Active' : 'Inactive'}
                    </span>
                </div>
            </div>

            <button
                onClick={onTest}
                className="w-full mt-4 flex items-center justify-center space-x-2 px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-all"
            >
                <RefreshCw className="w-4 h-4" />
                <span>Test Connection</span>
            </button>
        </div>
    );
};

export default Settings;
