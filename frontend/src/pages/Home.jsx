import { Link } from 'react-router-dom';
import { ArrowRight, Layers, Zap, Download } from 'lucide-react';

export default function Home() {
    return (
        <div className="flex flex-col min-h-screen">
            <header className="px-6 py-4 flex justify-between items-center border-b border-gray-800">
                <div className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600">
                    TextileAI
                </div>
                <div className="space-x-4">
                    <Link to="/login" className="text-gray-300 hover:text-white transition">Login</Link>
                    <Link to="/signup" className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition">
                        Get Started
                    </Link>
                </div>
            </header>

            <main className="flex-grow">
                <section className="py-20 text-center px-4">
                    <h1 className="text-5xl md:text-7xl font-extrabold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500">
                        Upscale Images for <br /> Textile Printing
                    </h1>
                    <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
                        Transform low-resolution designs into production-ready 16K TIFF files using advanced AI models.
                    </p>
                    <Link to="/signup" className="inline-flex items-center bg-white text-gray-900 px-8 py-4 rounded-full font-bold text-lg hover:bg-gray-100 transition">
                        Start Upscaling <ArrowRight className="ml-2" />
                    </Link>
                </section>

                <section className="py-20 bg-gray-800/50">
                    <div className="max-w-6xl mx-auto px-6 grid md:grid-cols-3 gap-10">
                        <div className="p-6 bg-gray-800 rounded-xl border border-gray-700">
                            <Zap className="w-12 h-12 text-yellow-400 mb-4" />
                            <h3 className="text-xl font-bold mb-2">AI Super-Resolution</h3>
                            <p className="text-gray-400">Upscale up to 16K using Real-ESRGAN and SwinIR models.</p>
                        </div>
                        <div className="p-6 bg-gray-800 rounded-xl border border-gray-700">
                            <Layers className="w-12 h-12 text-purple-400 mb-4" />
                            <h3 className="text-xl font-bold mb-2">Textile Optimization</h3>
                            <p className="text-gray-400">Enhance fine details specifically for fabric printing patterns.</p>
                        </div>
                        <div className="p-6 bg-gray-800 rounded-xl border border-gray-700">
                            <Download className="w-12 h-12 text-green-400 mb-4" />
                            <h3 className="text-xl font-bold mb-2">Production Ready</h3>
                            <p className="text-gray-400">Export as 16-bit TIFF with customizable PPI (200-300).</p>
                        </div>
                    </div>
                </section>
            </main>

            <footer className="py-8 text-center text-gray-500 border-t border-gray-800">
                © 2024 TextileAI. Open Source Project.
            </footer>
        </div>
    );
}
