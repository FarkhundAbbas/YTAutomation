import React, { useEffect, useState } from 'react';
import { FileText, CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react';

interface Proposal {
    id: number;
    error_group_id: number;
    candidate_patterns: Array<{
        pattern: string;
        pattern_type: string;
        confidence: number;
        platform: string;
    }>;
    validation_scores: {
        parse_rate: number;
        accuracy: number;
    };
    status: string;
    created_at: string;
}

const Proposals: React.FC = () => {
    const [proposals, setProposals] = useState<Proposal[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedProposal, setSelectedProposal] = useState<Proposal | null>(null);
    const [selectedPattern, setSelectedPattern] = useState<number>(0);

    useEffect(() => {
        loadProposals();
    }, []);

    const loadProposals = async () => {
        try {
            // Mock data for demo
            const mockProposals: Proposal[] = [
                {
                    id: 1,
                    error_group_id: 101,
                    candidate_patterns: [
                        {
                            pattern: '^(?<timestamp>\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}) (?<level>\\w+) (?<message>.+)$',
                            pattern_type: 'regex',
                            confidence: 0.95,
                            platform: 'generic'
                        },
                        {
                            pattern: '%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}',
                            pattern_type: 'grok',
                            confidence: 0.92,
                            platform: 'elastic'
                        }
                    ],
                    validation_scores: {
                        parse_rate: 0.98,
                        accuracy: 0.96
                    },
                    status: 'pending',
                    created_at: new Date().toISOString()
                },
                {
                    id: 2,
                    error_group_id: 102,
                    candidate_patterns: [
                        {
                            pattern: '^(?<ip>\\d+\\.\\d+\\.\\d+\\.\\d+) - - \\[(?<timestamp>[^\\]]+)\\] "(?<method>\\w+) (?<path>[^"]+)" (?<status>\\d+) (?<bytes>\\d+)$',
                            pattern_type: 'regex',
                            confidence: 0.89,
                            platform: 'generic'
                        }
                    ],
                    validation_scores: {
                        parse_rate: 0.94,
                        accuracy: 0.91
                    },
                    status: 'approved',
                    created_at: new Date(Date.now() - 86400000).toISOString()
                }
            ];
            setProposals(mockProposals);
        } catch (error) {
            console.error('Failed to load proposals:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleApprove = (proposalId: number, patternIndex: number) => {
        console.log(`Approving proposal ${proposalId}, pattern ${patternIndex}`);
        setProposals(proposals.map(p =>
            p.id === proposalId ? { ...p, status: 'approved' } : p
        ));
    };

    const handleReject = (proposalId: number) => {
        console.log(`Rejecting proposal ${proposalId}`);
        setProposals(proposals.map(p =>
            p.id === proposalId ? { ...p, status: 'rejected' } : p
        ));
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-cyan-500 border-t-transparent"></div>
                    <p className="text-gray-400 mt-4">Loading proposals...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-cyan-100 to-blue-200 bg-clip-text text-transparent mb-2">
                    Pattern Proposals
                </h1>
                <p className="text-gray-400">Review and approve AI-generated parsing patterns</p>
            </div>

            {/* Proposals Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Proposals List */}
                <div className="space-y-4">
                    <h2 className="text-xl font-semibold text-white mb-4">All Proposals</h2>
                    {proposals.map((proposal) => (
                        <ProposalCard
                            key={proposal.id}
                            proposal={proposal}
                            isSelected={selectedProposal?.id === proposal.id}
                            onClick={() => setSelectedProposal(proposal)}
                        />
                    ))}
                </div>

                {/* Proposal Details */}
                {selectedProposal && (
                    <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-slate-700/50 sticky top-8">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-semibold text-white">Proposal Details</h2>
                            <StatusBadge status={selectedProposal.status} />
                        </div>

                        {/* Pattern Selector */}
                        <div className="mb-6">
                            <label className="text-sm font-medium text-gray-400 mb-2 block">
                                Select Pattern ({selectedProposal.candidate_patterns.length} options)
                            </label>
                            <div className="flex space-x-2">
                                {selectedProposal.candidate_patterns.map((_, index) => (
                                    <button
                                        key={index}
                                        onClick={() => setSelectedPattern(index)}
                                        className={`px-4 py-2 rounded-lg transition-all ${selectedPattern === index
                                            ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white'
                                            : 'bg-slate-700/50 text-gray-400 hover:bg-slate-700'
                                            }`}
                                    >
                                        Pattern {index + 1}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Pattern Details */}
                        <div className="space-y-4">
                            <div>
                                <label className="text-sm font-medium text-gray-400 mb-2 block">Pattern</label>
                                <div className="bg-slate-900/50 rounded-lg p-4 font-mono text-sm text-cyan-400 overflow-x-auto">
                                    {selectedProposal.candidate_patterns[selectedPattern].pattern}
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-sm font-medium text-gray-400 mb-2 block">Type</label>
                                    <div className="bg-slate-900/50 rounded-lg p-3 text-white">
                                        {selectedProposal.candidate_patterns[selectedPattern].pattern_type}
                                    </div>
                                </div>
                                <div>
                                    <label className="text-sm font-medium text-gray-400 mb-2 block">Platform</label>
                                    <div className="bg-slate-900/50 rounded-lg p-3 text-white">
                                        {selectedProposal.candidate_patterns[selectedPattern].platform}
                                    </div>
                                </div>
                            </div>

                            <div>
                                <label className="text-sm font-medium text-gray-400 mb-2 block">Confidence Score</label>
                                <div className="flex items-center space-x-3">
                                    <div className="flex-1 bg-slate-900/50 rounded-full h-3 overflow-hidden">
                                        <div
                                            className="h-full bg-gradient-to-r from-cyan-500 to-blue-600"
                                            style={{ width: `${selectedProposal.candidate_patterns[selectedPattern].confidence * 100}%` }}
                                        ></div>
                                    </div>
                                    <span className="text-white font-semibold">
                                        {(selectedProposal.candidate_patterns[selectedPattern].confidence * 100).toFixed(1)}%
                                    </span>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-sm font-medium text-gray-400 mb-2 block">Parse Rate</label>
                                    <div className="text-2xl font-bold text-green-400">
                                        {(selectedProposal.validation_scores.parse_rate * 100).toFixed(1)}%
                                    </div>
                                </div>
                                <div>
                                    <label className="text-sm font-medium text-gray-400 mb-2 block">Accuracy</label>
                                    <div className="text-2xl font-bold text-blue-400">
                                        {(selectedProposal.validation_scores.accuracy * 100).toFixed(1)}%
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Actions */}
                        {selectedProposal.status === 'pending' && (
                            <div className="flex space-x-3 mt-6">
                                <button
                                    onClick={() => handleApprove(selectedProposal.id, selectedPattern)}
                                    className="flex-1 flex items-center justify-center space-x-2 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl hover:from-green-600 hover:to-emerald-700 transition-all shadow-lg"
                                >
                                    <CheckCircle className="w-5 h-5" />
                                    <span className="font-medium">Approve</span>
                                </button>
                                <button
                                    onClick={() => handleReject(selectedProposal.id)}
                                    className="flex-1 flex items-center justify-center space-x-2 px-6 py-3 bg-gradient-to-r from-red-500 to-orange-600 text-white rounded-xl hover:from-red-600 hover:to-orange-700 transition-all shadow-lg"
                                >
                                    <XCircle className="w-5 h-5" />
                                    <span className="font-medium">Reject</span>
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

interface ProposalCardProps {
    proposal: Proposal;
    isSelected: boolean;
    onClick: () => void;
}

const ProposalCard: React.FC<ProposalCardProps> = ({ proposal, isSelected, onClick }) => {
    return (
        <div
            onClick={onClick}
            className={`bg-slate-800/50 backdrop-blur-sm rounded-xl p-5 shadow-lg border transition-all cursor-pointer ${isSelected
                ? 'border-cyan-500 shadow-cyan-500/20'
                : 'border-slate-700/50 hover:border-slate-600'
                }`}
        >
            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                    <div className="p-2 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg">
                        <FileText className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h3 className="text-white font-semibold">Proposal #{proposal.id}</h3>
                        <p className="text-sm text-gray-400">Error Group #{proposal.error_group_id}</p>
                    </div>
                </div>
                <StatusBadge status={proposal.status} />
            </div>

            <div className="grid grid-cols-3 gap-3 text-sm">
                <div>
                    <p className="text-gray-400 mb-1">Patterns</p>
                    <p className="text-white font-semibold">{proposal.candidate_patterns.length}</p>
                </div>
                <div>
                    <p className="text-gray-400 mb-1">Parse Rate</p>
                    <p className="text-green-400 font-semibold">
                        {(proposal.validation_scores.parse_rate * 100).toFixed(0)}%
                    </p>
                </div>
                <div>
                    <p className="text-gray-400 mb-1">Accuracy</p>
                    <p className="text-blue-400 font-semibold">
                        {(proposal.validation_scores.accuracy * 100).toFixed(0)}%
                    </p>
                </div>
            </div>
        </div>
    );
};

const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
    const getStatusConfig = () => {
        switch (status) {
            case 'pending':
                return { icon: Clock, text: 'Pending', className: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30' };
            case 'approved':
                return { icon: CheckCircle, text: 'Approved', className: 'bg-green-500/10 text-green-400 border-green-500/30' };
            case 'rejected':
                return { icon: XCircle, text: 'Rejected', className: 'bg-red-500/10 text-red-400 border-red-500/30' };
            default:
                return { icon: AlertCircle, text: status, className: 'bg-gray-500/10 text-gray-400 border-gray-500/30' };
        }
    };

    const config = getStatusConfig();
    const Icon = config.icon;

    return (
        <div className={`flex items-center space-x-1 px-3 py-1 rounded-full border text-xs font-medium ${config.className}`}>
            <Icon className="w-3 h-3" />
            <span>{config.text}</span>
        </div>
    );
};

export default Proposals;
