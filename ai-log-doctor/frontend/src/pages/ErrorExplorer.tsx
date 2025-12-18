import React, { useEffect, useState } from 'react';
import { AlertCircle, FileText, Sparkles } from 'lucide-react';
import axios from 'axios';

interface ErrorGroup {
    error_group_id: number;
    hash: string;
    log_count: number;
    sample_logs: string[];
}

const ErrorExplorer: React.FC = () => {
    const [errorGroups, setErrorGroups] = useState<ErrorGroup[]>([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState<number | null>(null);

    useEffect(() => {
        loadErrorGroups();
    }, []);

    const loadErrorGroups = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get('http://localhost:8002/error-groups', {
                headers: { Authorization: `Bearer ${token}` },
            });
            setErrorGroups(response.data);
        } catch (error) {
            console.error('Failed to load error groups:', error);
        } finally {
            setLoading(false);
        }
    };

    const generateFix = async (errorGroupId: number) => {
        setGenerating(errorGroupId);
        try {
            const token = localStorage.getItem('token');
            const response = await axios.post(
                '/api/proposals/create',
                null,
                {
                    params: { error_group_id: errorGroupId, platform: 'generic' },
                    headers: { Authorization: `Bearer ${token}` },
                }
            );
            alert(`Proposal created! ID: ${response.data.proposal_id}`);
        } catch (error) {
            console.error('Failed to generate fix:', error);
            alert('Failed to generate fix');
        } finally {
            setGenerating(null);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-gray-400">Loading error groups...</div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold text-white">Error Explorer</h1>
                <button
                    onClick={loadErrorGroups}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                >
                    Refresh
                </button>
            </div>

            {errorGroups.length === 0 ? (
                <div className="bg-slate-800 rounded-xl p-12 text-center border border-slate-700">
                    <FileText className="w-16 h-16 text-gray-500 mx-auto mb-4" />
                    <p className="text-gray-400 text-lg">No error groups found</p>
                    <p className="text-gray-500 text-sm mt-2">Start ingesting logs to see errors here</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-4">
                    {errorGroups.map((group) => (
                        <div
                            key={group.error_group_id}
                            className="bg-slate-800 rounded-xl p-6 shadow-xl border border-slate-700 hover:border-red-500/50 transition-all"
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center space-x-3">
                                    <AlertCircle className="w-6 h-6 text-red-500" />
                                    <div>
                                        <h3 className="text-lg font-semibold text-white">
                                            Error Group #{group.error_group_id}
                                        </h3>
                                        <p className="text-gray-400 text-sm">Hash: {group.hash}</p>
                                    </div>
                                </div>
                                <div className="flex items-center space-x-3">
                                    <span className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-sm font-medium">
                                        {group.log_count} logs
                                    </span>
                                    <button
                                        onClick={() => generateFix(group.error_group_id)}
                                        disabled={generating === group.error_group_id}
                                        className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
                                    >
                                        <Sparkles className="w-4 h-4" />
                                        <span>{generating === group.error_group_id ? 'Generating...' : 'Generate Fix'}</span>
                                    </button>
                                </div>
                            </div>

                            <div className="bg-slate-900 rounded-lg p-4 space-y-2">
                                <p className="text-gray-400 text-sm font-semibold mb-2">Sample Logs:</p>
                                {group.sample_logs.slice(0, 3).map((log, idx) => (
                                    <div key={idx} className="bg-slate-950 p-2 rounded font-mono text-xs text-gray-300 overflow-x-auto">
                                        {log}
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default ErrorExplorer;
