import React from 'react';
import Navbar from '../components/Navbar';
import Hero from '../components/Hero';
import HowItWorks from '../components/HowItWorks';
import AnalyzerChat from '../components/AnalyzerChat';
import MeshBackground from '../components/MeshBackground';
import useHealthCheck from '../hooks/useHealthCheck';

const Home = () => {
    const healthStatus = useHealthCheck();

    return (
        <div className="relative min-h-screen bg-[#0D0D0D]">
            <MeshBackground />
            <Navbar healthStatus={healthStatus} />
            <main>
                <Hero />
                <HowItWorks />
                <AnalyzerChat />
            </main>

            <footer className="py-12 border-t border-white/5 bg-[#0D0D0D]">
                <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
                    <div className="flex items-center gap-2">
                        <span className="text-sm font-black tracking-widest text-[#F5F5F7] uppercase">
                            CCPA <span className="text-[#CBFB45]">Compliance</span>
                        </span>
                    </div>
                    <p className="text-[#F5F5F7]/40 text-[10px] font-black uppercase tracking-widest text-center">
                        © 2026 CCPA Compliance Analyzer. Powered by AI Legal Intelligence.
                    </p>
                    <div className="flex gap-6">
                        <a href="#" className="text-[#F5F5F7]/40 hover:text-[#CBFB45] transition-colors text-[10px] font-black uppercase tracking-widest">Privacy Policy</a>
                        <a href="#" className="text-[#F5F5F7]/40 hover:text-[#CBFB45] transition-colors text-[10px] font-black uppercase tracking-widest">Terms of Service</a>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default Home;
