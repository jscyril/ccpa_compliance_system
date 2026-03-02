import React from 'react';
import { motion } from 'framer-motion';
import { ChevronRight, Sparkles, Shield } from 'lucide-react';

const Hero = () => {
    const scrollToAnalyzer = () => {
        document.getElementById('analyzer')?.scrollIntoView({ behavior: 'smooth' });
    };

    return (
        <section id="home" className="relative min-h-screen flex items-center pt-24 pb-16 overflow-x-hidden">
            <div className="max-w-7xl mx-auto px-6 w-full">
                {/* Two-column layout — text left, graphic right */}
                <div className="grid grid-cols-1 lg:grid-cols-[55%_45%] gap-8 items-center">

                    {/* ── Left: Text Content ─────────────────────────────────── */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, ease: [0.23, 1, 0.32, 1] }}
                        className="flex flex-col gap-8 pr-0 lg:pr-8"
                    >
                        {/* Badge */}
                        <div className="inline-flex w-fit items-center gap-2 px-3 py-1.5 bg-[#CBFB45]/10 border border-[#CBFB45]/20">
                            <Sparkles className="w-3 h-3 text-[#CBFB45] shrink-0" />
                            <span className="text-[10px] font-black tracking-[0.3em] text-[#CBFB45] uppercase">
                                Enterprise AI Compliance
                            </span>
                        </div>

                        {/* Headline — constrained so it never bleeds right */}
                        <h1 className="font-black leading-[0.88] uppercase tracking-tighter text-[clamp(3rem,7vw,6.5rem)]">
                            <span className="block text-[#F5F5F7]">AI Legal</span>
                            <span className="block text-[#CBFB45]">Intelligence</span>
                            <span className="block text-[#F5F5F7]">Platform</span>
                        </h1>

                        {/* Description */}
                        <p className="text-base lg:text-lg text-[#F5F5F7]/55 font-medium leading-relaxed max-w-lg">
                            Redefining CCPA compliance with data-first, automated legal reasoning.
                            Analyze business practices against California statutes with precision.
                        </p>

                        {/* CTA */}
                        <div className="flex flex-wrap gap-4">
                            <button
                                onClick={scrollToAnalyzer}
                                className="btn-pulsr px-10 py-5 flex items-center gap-3 group shrink-0"
                            >
                                <span>Start Analysis</span>
                                <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                            </button>
                            <button
                                onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
                                className="px-10 py-5 border border-white/10 text-[#F5F5F7]/60 font-black text-xs uppercase tracking-widest hover:border-[#CBFB45]/40 hover:text-[#CBFB45] transition-all"
                            >
                                How it Works
                            </button>
                        </div>
                    </motion.div>

                    {/* ── Right: Geometric Graphic ───────────────────────────── */}
                    <motion.div
                        initial={{ opacity: 0, x: 40 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 1, delay: 0.25 }}
                        className="hidden lg:flex items-center justify-center"
                    >
                        {/* Neon border wrapper */}
                        <div className="w-full max-w-[420px] p-[1px] bg-gradient-to-br from-[#CBFB45]/30 to-transparent">
                            <div className="relative aspect-[4/5] bg-[#0D0D0D] flex items-center justify-center border border-white/5 overflow-hidden">
                                {/* Internal grid */}
                                <div className="absolute inset-0 grid-overlay opacity-10" />

                                {/* Rotating rings */}
                                <motion.div
                                    animate={{ rotate: [0, 360] }}
                                    transition={{ duration: 60, repeat: Infinity, ease: 'linear' }}
                                    className="absolute w-64 h-64 border border-[#CBFB45]/20 rounded-full"
                                />
                                <motion.div
                                    animate={{ rotate: [360, 0] }}
                                    transition={{ duration: 40, repeat: Infinity, ease: 'linear' }}
                                    className="absolute w-44 h-44 border border-[#CBFB45]/10 rounded-full"
                                />

                                {/* Shield icon */}
                                <Shield className="w-28 h-28 text-[#CBFB45]/15 z-10" strokeWidth={0.5} />

                                {/* Scan line animation */}
                                <motion.div
                                    animate={{ y: ['-100%', '100%'] }}
                                    transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
                                    className="absolute inset-x-0 h-[2px] bg-gradient-to-r from-transparent via-[#CBFB45]/25 to-transparent"
                                />

                                {/* Top / bottom accent lines */}
                                <div className="absolute top-0 inset-x-0 h-[1px] bg-gradient-to-r from-transparent via-[#CBFB45]/20 to-transparent" />
                                <div className="absolute bottom-0 inset-x-0 h-[1px] bg-gradient-to-r from-transparent via-[#CBFB45]/20 to-transparent" />
                            </div>
                        </div>
                    </motion.div>
                </div>
            </div>
        </section>
    );
};

export default Hero;
