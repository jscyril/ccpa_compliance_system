import React, { useState, useEffect, useRef } from 'react';
import { Shield } from 'lucide-react';

// ── Text Scramble Hook (AlphaWave style) ──────────────────────────────────────
const CHARS = '!<>-_\\/[]{}—=+*^?#ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';

function useScramble(text, trigger) {
    const [display, setDisplay] = useState(text);
    const frameRef = useRef(null);

    useEffect(() => {
        if (!trigger) {
            setDisplay(text);
            return;
        }

        let iteration = 0;
        const totalFrames = text.length * 3;

        clearInterval(frameRef.current);
        frameRef.current = setInterval(() => {
            setDisplay(
                text
                    .split('')
                    .map((char, idx) => {
                        if (char === ' ') return ' ';
                        if (idx < iteration / 3) return char;
                        return CHARS[Math.floor(Math.random() * CHARS.length)];
                    })
                    .join('')
            );

            if (iteration >= totalFrames) {
                clearInterval(frameRef.current);
                setDisplay(text);
            }
            iteration++;
        }, 25);

        return () => clearInterval(frameRef.current);
    }, [trigger, text]);

    return display;
}

// ── Scramble Nav Link ─────────────────────────────────────────────────────────
const ScrambleLink = ({ label, onClick, isActive }) => {
    const [hovered, setHovered] = useState(false);
    const scrambled = useScramble(label, hovered);

    return (
        <button
            onClick={onClick}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
            className={`text-[11px] font-black uppercase tracking-[0.25em] transition-colors font-mono ${isActive ? 'text-[#CBFB45]' : 'text-[#F5F5F7]/50 hover:text-[#CBFB45]'
                }`}
        >
            {scrambled}
        </button>
    );
};

// ── Section Dot Indicator (right side, AlphaWave style) ────────────────────────
const SECTIONS = [
    { id: 'home', label: 'Home' },
    { id: 'how-it-works', label: 'How It Works' },
    { id: 'analyzer', label: 'Analyzer' },
];

const SideNav = ({ activeSection }) => (
    <div className="fixed right-6 top-1/2 -translate-y-1/2 z-50 flex flex-col items-center gap-4">
        {SECTIONS.map(({ id, label }) => {
            const isActive = activeSection === id;
            return (
                <button
                    key={id}
                    onClick={() => {
                        document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
                    }}
                    title={label}
                    className="group flex items-center gap-3"
                >
                    {/* Label (shows on hover, right-to-left) */}
                    <span className="opacity-0 group-hover:opacity-100 transition-opacity text-[9px] font-black uppercase tracking-widest text-[#CBFB45] translate-x-2 group-hover:translate-x-0 transition-transform">
                        {label}
                    </span>
                    {/* Diamond indicator */}
                    <div
                        className={`w-2.5 h-2.5 rotate-45 border transition-all duration-300 ${isActive
                                ? 'bg-[#CBFB45] border-[#CBFB45] scale-125'
                                : 'bg-transparent border-[#F5F5F7]/30 group-hover:border-[#CBFB45]'
                            }`}
                    />
                </button>
            );
        })}
    </div>
);

// ── Main Navbar ───────────────────────────────────────────────────────────────
const Navbar = ({ healthStatus }) => {
    const isOnline = healthStatus === 'healthy';
    const [activeSection, setActiveSection] = useState('home');

    // Track active section via IntersectionObserver
    useEffect(() => {
        const observers = SECTIONS.map(({ id }) => {
            const el = document.getElementById(id);
            if (!el) return null;

            const observer = new IntersectionObserver(
                ([entry]) => {
                    if (entry.isIntersecting) setActiveSection(id);
                },
                { rootMargin: '-40% 0px -40% 0px', threshold: 0 }
            );
            observer.observe(el);
            return observer;
        });

        return () => observers.forEach(o => o?.disconnect());
    }, []);

    const scrollTo = (id) => {
        document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
    };

    return (
        <>
            {/* Horizontal Navbar */}
            <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0D0D0D]/90 backdrop-blur-xl border-b border-white/5">
                <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between gap-6">
                    {/* Logo */}
                    <div
                        className="flex items-center gap-3 cursor-pointer shrink-0"
                        onClick={() => scrollTo('home')}
                    >
                        <div className="w-8 h-8 bg-[#CBFB45] flex items-center justify-center">
                            <Shield className="w-5 h-5 text-[#0D0D0D]" strokeWidth={2.5} />
                        </div>
                        <span className="text-sm font-black tracking-widest text-[#F5F5F7] uppercase font-mono">
                            CCPA <span className="text-[#CBFB45]">Compliance</span>
                        </span>
                    </div>

                    {/* Nav Links with scramble effect */}
                    <div className="hidden md:flex items-center gap-10">
                        {SECTIONS.map(({ id, label }) => (
                            <ScrambleLink
                                key={id}
                                label={label}
                                onClick={() => scrollTo(id)}
                                isActive={activeSection === id}
                            />
                        ))}
                    </div>

                    {/* Backend Status */}
                    <div
                        className={`flex items-center gap-2 px-3 py-1.5 border ${isOnline
                                ? 'border-[#34D399]/20 bg-[#34D399]/5'
                                : 'border-[#F87171]/20 bg-[#F87171]/5'
                            }`}
                    >
                        <div
                            className={`w-1.5 h-1.5 rounded-full ${isOnline ? 'bg-[#34D399] animate-pulse' : 'bg-[#F87171]'
                                }`}
                        />
                        <span
                            className={`text-[10px] font-black uppercase tracking-widest font-mono ${isOnline ? 'text-[#34D399]' : 'text-[#F87171]'
                                }`}
                        >
                            {isOnline ? 'System Live' : 'Backend Offline'}
                        </span>
                    </div>
                </div>
            </nav>

            {/* Right Side Diamond Nav */}
            <SideNav activeSection={activeSection} />
        </>
    );
};

export default Navbar;
