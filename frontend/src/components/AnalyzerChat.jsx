import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, Loader2, Info, CornerDownLeft } from 'lucide-react';
import { analyzePolicyStream } from '../services/api';
import toast from 'react-hot-toast';
import VerdictCard from './VerdictCard';

// ── Typing Cursor ─────────────────────────────────────────────────────────────
const Cursor = () => (
    <motion.span
        animate={{ opacity: [1, 0, 1] }}
        transition={{ duration: 0.8, repeat: Infinity, ease: 'easeInOut' }}
        className="inline-block w-[2px] h-4 bg-[#CBFB45] ml-0.5 align-middle"
    />
);

// ── Message Bubble ─────────────────────────────────────────────────────────────
const Bubble = ({ msg, isStreaming }) => {
    const isUser = msg.type === 'user';

    return (
        <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, ease: [0.23, 1, 0.32, 1] }}
            className={`flex gap-4 ${isUser ? 'justify-end' : 'justify-start'}`}
        >
            {/* Bot Avatar */}
            {!isUser && (
                <div className="w-8 h-8 shrink-0 bg-[#CBFB45] flex items-center justify-center mt-1">
                    <Zap className="w-4 h-4 text-[#0D0D0D] fill-current" />
                </div>
            )}

            <div className={`max-w-[80%] ${isUser ? 'items-end' : 'items-start'} flex flex-col gap-4`}>
                {/* Text Content */}
                <div className={`px-5 py-4 text-sm leading-relaxed ${isUser
                    ? 'bg-[#CBFB45] text-[#0D0D0D] font-bold'
                    : 'bg-[#1A1A1A] text-[#F5F5F7]/80 border border-white/5'
                    }`}>
                    {isUser ? (
                        <>
                            <div className="text-[9px] font-black uppercase tracking-[0.25em] opacity-40 mb-1">Query</div>
                            {msg.content}
                        </>
                    ) : (
                        <>
                            <div className="text-[9px] font-black uppercase tracking-[0.25em] text-[#CBFB45] mb-1">
                                Agent
                            </div>
                            <span>{msg.content}</span>
                            {isStreaming && <Cursor />}
                        </>
                    )}
                </div>

                {/* Verdict Card (shown after streaming completes) */}
                {msg.verdict && !isStreaming && (
                    <motion.div
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="w-full"
                    >
                        <VerdictCard verdict={msg.verdict} />
                    </motion.div>
                )}
            </div>

            {/* User Avatar */}
            {isUser && (
                <div className="w-8 h-8 shrink-0 bg-[#333] flex items-center justify-center mt-1">
                    <span className="text-[10px] font-black text-white/50">U</span>
                </div>
            )}
        </motion.div>
    );
};

// ── Main Component ─────────────────────────────────────────────────────────────
const AnalyzerChat = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isStreaming, setIsStreaming] = useState(false);
    const scrollRef = useRef(null);
    const inputRef = useRef(null);

    // Auto-scroll on new content
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleAnalyze = async (e) => {
        e?.preventDefault();
        const trimmed = input.trim();
        if (!trimmed || isStreaming) return;

        // Add user message
        setMessages(prev => [...prev, { type: 'user', content: trimmed }]);
        setInput('');
        setIsStreaming(true);

        // Add empty bot message to stream into
        const botId = Date.now();
        setMessages(prev => [...prev, { id: botId, type: 'bot', content: '', verdict: null }]);

        try {
            await analyzePolicyStream(
                trimmed,
                // onChunk: stream text into the last bot message
                (chunk) => {
                    setMessages(prev =>
                        prev.map(m =>
                            m.id === botId
                                ? { ...m, content: m.content + chunk }
                                : m
                        )
                    );
                },
                // onDone: attach verdict card
                (result) => {
                    setMessages(prev =>
                        prev.map(m =>
                            m.id === botId
                                ? {
                                    ...m,
                                    content: result.harmful
                                        ? '⚠️  Risk detected. See the compliance verdict below.'
                                        : '✅  This practice appears to be compliant. See the verdict below.',
                                    verdict: {
                                        harmful: result.harmful,
                                        articles: result.articles ?? [],
                                        referenced_articles: result.referenced_articles ?? [],
                                    },
                                }
                                : m
                        )
                    );
                }
            );
        } catch (err) {
            setMessages(prev =>
                prev.map(m =>
                    m.id === botId
                        ? { ...m, content: '⚠️  Connection failed. Make sure the backend is running on localhost:8000.' }
                        : m
                )
            );
            toast.error('Backend unavailable', {
                style: {
                    background: '#1A1A1A',
                    color: '#F87171',
                    border: '1px solid rgba(248,113,113,0.2)',
                    borderRadius: 0,
                    fontSize: '10px',
                    fontWeight: 900,
                    textTransform: 'uppercase',
                    letterSpacing: '0.1em',
                },
            });
        } finally {
            setIsStreaming(false);
            setTimeout(() => inputRef.current?.focus(), 50);
        }
    };

    return (
        <section id="analyzer" className="py-32 relative bg-[#0D0D0D]">
            <div className="max-w-4xl mx-auto px-6">
                {/* Heading */}
                <div className="text-center mb-16">
                    <h2 className="text-4xl lg:text-5xl font-black text-[#F5F5F7] uppercase tracking-tighter mb-4">
                        Compliance{' '}
                        <span className="text-[#CBFB45]">Analyzer</span>
                    </h2>
                    <p className="text-[#F5F5F7]/40 text-xs uppercase tracking-[0.25em] font-black">
                        Real-time AI analysis with streaming responses
                    </p>
                </div>

                {/* Chat Container */}
                <div className="bg-[#111] border border-white/5 min-h-[520px] flex flex-col relative overflow-hidden">
                    {/* subtle grid */}
                    <div className="absolute inset-0 grid-overlay opacity-5 pointer-events-none" />

                    {/* Top bar */}
                    <div className="px-6 py-3 border-b border-white/5 bg-[#0D0D0D]/50 flex items-center gap-3">
                        <div className="flex gap-1.5">
                            <div className="w-2.5 h-2.5 rounded-full bg-[#F87171]/40" />
                            <div className="w-2.5 h-2.5 rounded-full bg-[#FBBF24]/40" />
                            <div className="w-2.5 h-2.5 rounded-full bg-[#34D399]/40" />
                        </div>
                        <span className="text-[9px] font-black uppercase tracking-[0.3em] text-[#F5F5F7]/20">
                            CCPA Compliance Terminal
                        </span>
                        {isStreaming && (
                            <div className="ml-auto flex items-center gap-2 text-[#CBFB45]">
                                <motion.div
                                    animate={{ scale: [1, 1.3, 1] }}
                                    transition={{ duration: 0.6, repeat: Infinity }}
                                    className="w-1.5 h-1.5 rounded-full bg-[#CBFB45]"
                                />
                                <span className="text-[9px] font-black uppercase tracking-widest">
                                    Streaming
                                </span>
                            </div>
                        )}
                    </div>

                    {/* Messages */}
                    <div
                        ref={scrollRef}
                        className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar relative z-10"
                        style={{ minHeight: 360 }}
                    >
                        {messages.length === 0 && (
                            <div className="flex flex-col items-center justify-center h-full text-center opacity-30 py-16">
                                <Info className="w-10 h-10 text-[#CBFB45] mb-4" strokeWidth={1} />
                                <p className="text-xs font-black uppercase tracking-widest max-w-xs leading-loose">
                                    Describe a business practice to begin analysis.
                                </p>
                                <p className="text-[10px] text-[#F5F5F7]/40 mt-2 max-w-xs">
                                    e.g. "We collect and sell user location data to third parties without explicit opt-out."
                                </p>
                            </div>
                        )}

                        <AnimatePresence initial={false}>
                            {messages.map((msg, i) => (
                                <Bubble
                                    key={msg.id ?? i}
                                    msg={msg}
                                    isStreaming={isStreaming && i === messages.length - 1 && msg.type === 'bot'}
                                />
                            ))}
                        </AnimatePresence>
                    </div>

                    {/* Input */}
                    <div className="p-4 border-t border-white/5 bg-[#0D0D0D]/80 relative z-10">
                        <form onSubmit={handleAnalyze} className="flex gap-3">
                            <input
                                ref={inputRef}
                                type="text"
                                value={input}
                                onChange={e => setInput(e.target.value)}
                                disabled={isStreaming}
                                placeholder="Describe a business practice…"
                                className="flex-1 bg-[#1A1A1A] border border-white/10 py-4 px-5 text-sm text-[#F5F5F7] placeholder:text-white/20 focus:outline-none focus:border-[#CBFB45] transition-colors disabled:opacity-40"
                                onKeyDown={e => {
                                    if (e.key === 'Enter' && !e.shiftKey) {
                                        e.preventDefault();
                                        handleAnalyze();
                                    }
                                }}
                            />
                            <button
                                type="submit"
                                disabled={isStreaming || !input.trim()}
                                className="px-5 bg-[#CBFB45] text-[#0D0D0D] disabled:opacity-20 transition-opacity flex items-center gap-2 font-black text-xs uppercase tracking-widest"
                            >
                                {isStreaming ? (
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                ) : (
                                    <>
                                        <span>Analyze</span>
                                        <CornerDownLeft className="w-3.5 h-3.5" />
                                    </>
                                )}
                            </button>
                        </form>
                        <p className="text-[9px] text-[#F5F5F7]/20 mt-2 uppercase tracking-widest font-black">
                            Responses stream in real-time from the AI engine · Backend: localhost:8000
                        </p>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default AnalyzerChat;
