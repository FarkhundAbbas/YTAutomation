import React, { useEffect, useState } from 'react';
import { CheckCircle, XCircle, TrendingUp, BarChart3, FileCheck } from 'lucide-react';

interface ValidationReport {
    id: number;
    proposal_id: number;
    pattern: string;
    test_results: {
        total_logs: number;
        parsed_successfully: number;
        parse_failures: number;
        parse_rate: number;
        accuracy: number;
        false_positives: number;
        false_negatives: number;
    };
    sample_results: Array<{
        log: string;
        parsed: boolean;
        extracted_fields?: Record<string, string>;
        error?: string;
    }>;
    created_at: string;
}

const Validation: React.FC = () => {
    const [reports, setReports] = useState<ValidationReport[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedReport, setSelectedReport] = useState<ValidationReport | null>(null);

    useEffect(() => {
        loadReports();
    }, []);

    const loadReports = async () => {
        try {
            // Mock data for demo
            const mockReports: ValidationReport[] = [
                {
                    id: 1,
                    proposal_id: 1,
                    pattern: '^(?<timestamp>\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}) (?<level>\\w+) (?<message>.+)$',
                    test_results: {
                        total_logs: 1000,
                        parsed_successfully: 980,
                        parse_failures: 20,
                        parse_rate: 0.98,
                        accuracy: 0.96,
                        false_positives: 15,
                        false_negatives: 25
                    },
                    sample_results: [
                        {
                            log: '2024-01-15T10:30:45 INFO Application started successfully',
                            parsed: true,
                            extracted_fields: {
                                timestamp: '2024-01-15T10:30:45',
                                level: 'INFO',
                                message: 'Application started successfully'
                            }
                        },
                        {
                            log: '2024-01-15T10:31:12 ERROR Database connection failed',
                            parsed: true,
                            extracted_fields: {
                                timestamp: '2024-01-15T10:31:12',
                                level: 'ERROR',
                                message: 'Database connection failed'
                            }
                        },
                        {
                            log: 'Invalid log format without timestamp',
                            parsed: false,
                            error: 'Pattern does not match'
                        }
                    ],
                    created_at: new Date().toISOString()
                },
                {
                    id: 2,
                    proposal_id: 2,
                    pattern: '^(?<ip>\\d+\\.\\d+\\.\\d+\\.\\d+) - - \\[(?<timestamp>[^\\]]+)\\] "(?<method>\\w+) (?<path>[^"]+)" (?<status>\\d+) (?<bytes>\\d+)$',
                    test_results: {
                        total_logs: 500,
                        parsed_successfully: 470,
                        parse_failures: 30,
                        parse_rate: 0.94,
                        accuracy: 0.91,
                        false_positives: 20,
                        false_negatives: 25
                    },
                    sample_results: [
                        {
                            log: '192.168.1.1 - - [15/Jan/2024:10:30:45 +0000] "GET /api/users" 200 1234',
                            parsed: true,
                            extracted_fields: {
                                ip: '192.168.1.1',
                                timestamp: '15/Jan/2024:10:30:45 +0000',
                                method: 'GET',
                                path: '/api/users',
                                status: '200',
                                bytes: '1234'
                            }
                        }
                    ],
                    created_at: new Date(Date.now() - 86400000).toISOString()
                }
            ];
            setReports(mockReports);
            if (mockReports.length > 0) {
                setSelectedReport(mockReports[0]);
            }
        } catch (error) {
            console.error('Failed to load validation reports:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-cyan-500 border-t-transparent"></div>
                    <p className="text-gray-400 mt-4">Loading validation reports...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-cyan-100 to-blue-200 bg-clip-text text-transparent mb-2">
                    Pattern Validation
                </h1>
                <p className="text-gray-400">Review pattern testing results and accuracy metrics</p>
            </div>

            {/* Stats Overview */}
            {selectedReport && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <StatCard
                        icon={<BarChart3 className="w-6 h-6" />}
                        title="Total Logs Tested"
                        value={selectedReport.test_results.total_logs.toLocaleString()}
                        gradient="from-cyan-500 to-blue-600"
                    />
                    <StatCard
                        icon={<CheckCircle className="w-6 h-6" />}
                        title="Parse Rate"
                        value={`${(selectedReport.test_results.parse_rate * 100).toFixed(1)}%`}
                        gradient="from-green-500 to-emerald-600"
                    />
                    <StatCard
                        icon={<TrendingUp className="w-6 h-6" />}
                        title="Accuracy"
                        value={`${(selectedReport.test_results.accuracy * 100).toFixed(1)}%`}
                        gradient="from-blue-500 to-indigo-600"
                    />
                    <StatCard
                        icon={<XCircle className="w-6 h-6" />}
                        title="Parse Failures"
                        value={selectedReport.test_results.parse_failures.toString()}
                        gradient="from-red-500 to-orange-600"
                    />
                </div>
            )}

            {/* Reports Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Reports List */}
                <div className="space-y-4">
                    <h2 className="text-xl font-semibold text-white mb-4">Validation Reports</h2>
                    {reports.map((report) => (
                        <ReportCard
                            key={report.id}
                            report={report}
                            isSelected={selectedReport?.id === report.id}
                            onClick={() => setSelectedReport(report)}
                        />
                    ))}
                </div>

                {/* Report Details */}
                {selectedReport && (
                    <div className="lg:col-span-2 space-y-6">
                        {/* Pattern Display */}
                        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-slate-700/50">
                            <h3 className="text-lg font-semibold text-white mb-4">Pattern</h3>
                            <div className="bg-slate-900/50 rounded-lg p-4 font-mono text-sm text-cyan-400 overflow-x-auto">
                                {selectedReport.pattern}
                            </div>
                        </div>

                        {/* Test Results */}
                        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-slate-700/50">
                            <h3 className="text-lg font-semibold text-white mb-4">Test Results</h3>
                            <div className="grid grid-cols-2 gap-4">
                                <ResultItem
                                    label="Successfully Parsed"
                                    value={selectedReport.test_results.parsed_successfully}
                                    total={selectedReport.test_results.total_logs}
                                    color="text-green-400"
                                />
                                <ResultItem
                                    label="Parse Failures"
                                    value={selectedReport.test_results.parse_failures}
                                    total={selectedReport.test_results.total_logs}
                                    color="text-red-400"
                                />
                                <ResultItem
                                    label="False Positives"
                                    value={selectedReport.test_results.false_positives}
                                    total={selectedReport.test_results.total_logs}
                                    color="text-yellow-400"
                                />
                                <ResultItem
                                    label="False Negatives"
                                    value={selectedReport.test_results.false_negatives}
                                    total={selectedReport.test_results.total_logs}
                                    color="text-orange-400"
                                />
                            </div>
                        </div>

                        {/* Sample Results */}
                        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-slate-700/50">
                            <h3 className="text-lg font-semibold text-white mb-4">Sample Test Cases</h3>
                            <div className="space-y-4">
                                {selectedReport.sample_results.map((sample, index) => (
                                    <SampleResult key={index} sample={sample} />
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

interface StatCardProps {
    icon: React.ReactNode;
    title: string;
    value: string;
    gradient: string;
}

const StatCard: React.FC<StatCardProps> = ({ icon, title, value, gradient }) => {
    return (
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-5 shadow-lg border border-slate-700/50">
            <div className="flex items-center space-x-3 mb-3">
                <div className={`p-2 bg-gradient-to-br ${gradient} rounded-lg`}>
                    <div className="text-white">{icon}</div>
                </div>
                <p className="text-gray-400 text-sm">{title}</p>
            </div>
            <p className="text-3xl font-bold text-white">{value}</p>
        </div>
    );
};

interface ReportCardProps {
    report: ValidationReport;
    isSelected: boolean;
    onClick: () => void;
}

const ReportCard: React.FC<ReportCardProps> = ({ report, isSelected, onClick }) => {
    return (
        <div
            onClick={onClick}
            className={`bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 shadow-lg border transition-all cursor-pointer ${isSelected
                ? 'border-cyan-500 shadow-cyan-500/20'
                : 'border-slate-700/50 hover:border-slate-600'
                }`}
        >
            <div className="flex items-center space-x-3 mb-3">
                <div className="p-2 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg">
                    <FileCheck className="w-4 h-4 text-white" />
                </div>
                <div>
                    <h3 className="text-white font-semibold">Report #{report.id}</h3>
                    <p className="text-xs text-gray-400">Proposal #{report.proposal_id}</p>
                </div>
            </div>
            <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">Parse Rate:</span>
                <span className="text-green-400 font-semibold">
                    {(report.test_results.parse_rate * 100).toFixed(1)}%
                </span>
            </div>
        </div>
    );
};

interface ResultItemProps {
    label: string;
    value: number;
    total: number;
    color: string;
}

const ResultItem: React.FC<ResultItemProps> = ({ label, value, total, color }) => {
    const percentage = ((value / total) * 100).toFixed(1);
    return (
        <div className="bg-slate-900/50 rounded-lg p-4">
            <p className="text-gray-400 text-sm mb-2">{label}</p>
            <p className={`text-2xl font-bold ${color}`}>{value}</p>
            <p className="text-gray-500 text-xs mt-1">{percentage}% of total</p>
        </div>
    );
};

interface SampleResultProps {
    sample: {
        log: string;
        parsed: boolean;
        extracted_fields?: Record<string, string>;
        error?: string;
    };
}

const SampleResult: React.FC<SampleResultProps> = ({ sample }) => {
    return (
        <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/30">
            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2">
                    {sample.parsed ? (
                        <CheckCircle className="w-5 h-5 text-green-400" />
                    ) : (
                        <XCircle className="w-5 h-5 text-red-400" />
                    )}
                    <span className={`text-sm font-medium ${sample.parsed ? 'text-green-400' : 'text-red-400'}`}>
                        {sample.parsed ? 'Parsed Successfully' : 'Parse Failed'}
                    </span>
                </div>
            </div>
            <div className="mb-3">
                <p className="text-xs text-gray-400 mb-1">Log Entry:</p>
                <code className="text-sm text-gray-300 bg-slate-800 px-2 py-1 rounded block overflow-x-auto">
                    {sample.log}
                </code>
            </div>
            {sample.parsed && sample.extracted_fields && (
                <div>
                    <p className="text-xs text-gray-400 mb-2">Extracted Fields:</p>
                    <div className="grid grid-cols-2 gap-2">
                        {Object.entries(sample.extracted_fields).map(([key, value]) => (
                            <div key={key} className="bg-slate-800 rounded px-2 py-1">
                                <span className="text-xs text-cyan-400">{key}:</span>
                                <span className="text-xs text-white ml-1">{value}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
            {!sample.parsed && sample.error && (
                <div className="mt-2">
                    <p className="text-xs text-red-400">Error: {sample.error}</p>
                </div>
            )}
        </div>
    );
};

export default Validation;
