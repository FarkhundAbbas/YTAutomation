import { useState, useEffect } from 'react';
import api from '../api/axios';
import { Upload, Image as ImageIcon, Download, Loader2, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [scale, setScale] = useState(4);
    const [ppi, setPpi] = useState(250);
    const [enhance, setEnhance] = useState(false);
    const [loading, setLoading] = useState(false);
    const [jobId, setJobId] = useState(null);
    const [status, setStatus] = useState(null);
    const [exportFormat, setExportFormat] = useState('standard');
    const [bitDepth, setBitDepth] = useState(16);
    const [includeColorLayer, setIncludeColorLayer] = useState(true);
    const [exportLoading, setExportLoading] = useState(false);
    const navigate = useNavigate();

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setPreview(URL.createObjectURL(selectedFile));
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    const handleProcess = async () => {
        if (!file) return;
        setLoading(true);
        setStatus('uploading');

        const formData = new FormData();
        formData.append('file', file);
        formData.append('scale', scale);
        formData.append('ppi', ppi);
        formData.append('enhance', enhance);

        try {
            const res = await api.post('/process/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            setJobId(res.data.job_id);
            setStatus('pending');
        } catch (err) {
            console.error(err);
            setStatus('failed');
            setLoading(false);
        }
    };

    useEffect(() => {
        let interval;
        if (jobId && status !== 'completed' && status !== 'failed') {
            interval = setInterval(async () => {
                try {
                    const res = await api.get(`/process/status/${jobId}`);
                    setStatus(res.data.status);
                    if (res.data.status === 'completed' || res.data.status === 'failed') {
                        setLoading(false);
                        clearInterval(interval);
                    }
                } catch (err) {
                    console.error(err);
                }
            }, 2000);
        }
        return () => clearInterval(interval);
    }, [jobId, status]);

    const handleDownload = () => {
        if (!jobId) return;
        // Use nginx proxy path instead of direct backend access
        const downloadUrl = `/api/process/download/${jobId}`;
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.setAttribute('download', `enhanced_${jobId}.tiff`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const handleLayeredDownload = async () => {
        if (!jobId) return;
        setExportLoading(true);

        try {
            const response = await api.post('/export/layered-tiff', {
                job_id: jobId,
                ppi: ppi,
                include_color_layer: includeColorLayer,
                bit_depth: bitDepth
            }, {
                responseType: 'blob'
            });

            // Create download link
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `textile_layered_${jobId}.psd`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Layered TIFF export failed:', error);
            alert('Failed to export layered TIFF. Please try again.');
        } finally {
            setExportLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-900 p-6">
            <header className="flex justify-between items-center mb-10 max-w-6xl mx-auto">
                <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600">
                    Dashboard
                </h1>
                <button onClick={handleLogout} className="flex items-center text-gray-400 hover:text-white">
                    <LogOut className="w-5 h-5 mr-2" /> Logout
                </button>
            </header>

            <main className="max-w-6xl mx-auto grid md:grid-cols-2 gap-10">
                {/* Settings Panel */}
                <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 h-fit">
                    <h2 className="text-xl font-bold mb-6 flex items-center">
                        <ImageIcon className="w-6 h-6 mr-2 text-purple-400" /> Image Settings
                    </h2>

                    <div className="space-y-6">
                        <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center hover:border-purple-500 transition cursor-pointer relative">
                            <input
                                type="file"
                                onChange={handleFileChange}
                                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                accept="image/png, image/jpeg, image/jpg"
                            />
                            {preview ? (
                                <img src={preview} alt="Preview" className="max-h-48 mx-auto rounded" />
                            ) : (
                                <div className="text-gray-400">
                                    <Upload className="w-10 h-10 mx-auto mb-2" />
                                    <p>Click or Drag to Upload Image</p>
                                </div>
                            )}
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">Upscale Factor</label>
                            <select
                                value={scale}
                                onChange={(e) => setScale(Number(e.target.value))}
                                className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2"
                            >
                                <option value={4}>4x (Approx 8K)</option>
                                <option value={8}>8x (Approx 16K)</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">Output PPI</label>
                            <select
                                value={ppi}
                                onChange={(e) => setPpi(Number(e.target.value))}
                                className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2"
                            >
                                <option value={200}>200 PPI</option>
                                <option value={225}>225 PPI</option>
                                <option value={250}>250 PPI</option>
                                <option value={275}>275 PPI</option>
                                <option value={300}>300 PPI</option>
                            </select>
                        </div>

                        <div className="flex items-center">
                            <input
                                type="checkbox"
                                id="enhance"
                                checked={enhance}
                                onChange={(e) => setEnhance(e.target.checked)}
                                className="w-5 h-5 text-purple-600 rounded focus:ring-purple-500 bg-gray-700 border-gray-600"
                            />
                            <label htmlFor="enhance" className="ml-3 text-sm font-medium text-gray-300">
                                Apply Fine Detail Enhancement (SwinIR)
                            </label>
                        </div>

                        <button
                            onClick={handleProcess}
                            disabled={loading || !file}
                            className={`w-full py-3 rounded-lg font-bold text-white transition flex items-center justify-center ${loading || !file ? 'bg-gray-600 cursor-not-allowed' : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700'
                                }`}
                        >
                            {loading ? <Loader2 className="animate-spin mr-2" /> : null}
                            {loading ? 'Processing...' : 'Start Upscaling'}
                        </button>
                    </div>
                </div>

                {/* Results Panel */}
                <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 h-fit">
                    <h2 className="text-xl font-bold mb-6 flex items-center">
                        <Download className="w-6 h-6 mr-2 text-green-400" /> Results
                    </h2>

                    {status === 'completed' ? (
                        <div className="py-6">
                            <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Download className="w-10 h-10 text-green-500" />
                            </div>
                            <h3 className="text-2xl font-bold text-white mb-2 text-center">Processing Complete!</h3>
                            <p className="text-gray-400 mb-6 text-center">Your image has been upscaled and converted to TIFF.</p>

                            {/* Export Format Selection */}
                            <div className="space-y-4 mb-6">
                                <label className="block text-sm font-medium text-gray-300">Export Format</label>
                                <div className="space-y-2">
                                    <div className="flex items-center">
                                        <input
                                            type="radio"
                                            id="standard"
                                            name="exportFormat"
                                            value="standard"
                                            checked={exportFormat === 'standard'}
                                            onChange={(e) => setExportFormat(e.target.value)}
                                            className="w-4 h-4 text-purple-600 focus:ring-purple-500 bg-gray-700 border-gray-600"
                                        />
                                        <label htmlFor="standard" className="ml-3 text-sm text-gray-300">
                                            Standard TIFF (Single Layer)
                                        </label>
                                    </div>
                                    <div className="flex items-center">
                                        <input
                                            type="radio"
                                            id="layered"
                                            name="exportFormat"
                                            value="layered"
                                            checked={exportFormat === 'layered'}
                                            onChange={(e) => setExportFormat(e.target.value)}
                                            className="w-4 h-4 text-purple-600 focus:ring-purple-500 bg-gray-700 border-gray-600"
                                        />
                                        <label htmlFor="layered" className="ml-3 text-sm text-gray-300">
                                            Layered PSD (Photoshop Editable) ⭐
                                        </label>
                                    </div>
                                </div>
                            </div>

                            {/* Layered PSD Options */}
                            {exportFormat === 'layered' && (
                                <div className="space-y-4 mb-6 p-4 bg-gray-700/50 rounded-lg border border-gray-600">
                                    <h4 className="text-sm font-bold text-purple-400">Layered PSD Options</h4>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">Bit Depth</label>
                                        <select
                                            value={bitDepth}
                                            onChange={(e) => setBitDepth(Number(e.target.value))}
                                            className="w-full bg-gray-700 border border-gray-600 rounded px-4 py-2 text-white"
                                        >
                                            <option value={8}>8-bit (Standard)</option>
                                            <option value={16}>16-bit (Professional)</option>
                                        </select>
                                    </div>

                                    <div className="flex items-center">
                                        <input
                                            type="checkbox"
                                            id="colorLayer"
                                            checked={includeColorLayer}
                                            onChange={(e) => setIncludeColorLayer(e.target.checked)}
                                            className="w-5 h-5 text-purple-600 rounded focus:ring-purple-500 bg-gray-700 border-gray-600"
                                        />
                                        <label htmlFor="colorLayer" className="ml-3 text-sm font-medium text-gray-300">
                                            Include Color Correction Layer
                                        </label>
                                    </div>

                                    <div className="text-xs text-gray-400 mt-2">
                                        <p className="font-semibold mb-1">Included Layers:</p>
                                        <ul className="list-disc list-inside space-y-1">
                                            <li>Base Layer (Clean upscaled image)</li>
                                            <li>Detail Enhancement (High-frequency details)</li>
                                            <li>Pattern/Texture (Edge detection)</li>
                                            <li>Shadow Layer (Low-frequency shadows)</li>
                                            <li>Highlights Layer (High-frequency highlights)</li>
                                            {includeColorLayer && <li>Color Correction (LAB color space)</li>}
                                        </ul>
                                    </div>
                                </div>
                            )}

                            {/* Download Buttons */}
                            {exportFormat === 'standard' ? (
                                <button
                                    onClick={handleDownload}
                                    className="w-full bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-lg font-bold transition"
                                >
                                    Download Standard TIFF
                                </button>
                            ) : (
                                <button
                                    onClick={handleLayeredDownload}
                                    disabled={exportLoading}
                                    className={`w-full px-8 py-3 rounded-lg font-bold transition flex items-center justify-center ${exportLoading
                                        ? 'bg-gray-600 cursor-not-allowed'
                                        : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700'
                                        } text-white`}
                                >
                                    {exportLoading ? (
                                        <>
                                            <Loader2 className="animate-spin mr-2" />
                                            Generating Layers...
                                        </>
                                    ) : (
                                        'Download Layered PSD'
                                    )}
                                </button>
                            )}
                        </div>
                    ) : status === 'processing' || status === 'uploading' || status === 'pending' ? (
                        <div className="text-center py-10">
                            <Loader2 className="w-16 h-16 text-purple-500 animate-spin mx-auto mb-6" />
                            <h3 className="text-xl font-bold text-white mb-2">
                                {status === 'uploading' ? 'Uploading...' : 'Enhancing Image...'}
                            </h3>
                            <p className="text-gray-400">This might take a few moments depending on the resolution.</p>
                        </div>
                    ) : (
                        <div className="text-center py-20 text-gray-500 border-2 border-dashed border-gray-700 rounded-lg">
                            <p>Processed images will appear here</p>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}
