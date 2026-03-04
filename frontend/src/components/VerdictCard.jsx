import React from 'react';
import { CheckCircle, AlertTriangle, ExternalLink } from 'lucide-react';

const VerdictCard = ({ verdict }) => {
    const { harmful, articles, referenced_articles } = verdict;

    return (
        <div className={`p-6 border-l-4 ${harmful ? 'border-[#F87171] bg-[#F87171]/5' : 'border-[#34D399] bg-[#34D399]/5'} bg-[#151515] relative overflow-hidden group`}>
            {/* Background Glow */}
            <div className={`absolute -right-10 -top-10 w-32 h-32 rounded-full blur-3xl opacity-10 ${harmful ? 'bg-[#F87171]' : 'bg-[#34D399]'}`} />

            <div className="flex items-start gap-4 relative z-10">
                <div className={`p-2 rounded-none ${harmful ? 'bg-[#F87171]/20 text-[#F87171]' : 'bg-[#34D399]/20 text-[#34D399]'}`}>
                    {harmful ? <AlertTriangle className="w-5 h-5" /> : <CheckCircle className="w-5 h-5" />}
                </div>

                <div className="flex-1">
                    <h5 className={`text-sm font-black uppercase tracking-widest mb-1 ${harmful ? 'text-[#F87171]' : 'text-[#34D399]'}`}>
                        {harmful ? 'RISK DETECTED' : 'COMPLIANCE VERIFIED'}
                    </h5>
                    <p className="text-xl font-black text-[#F5F5F7] uppercase tracking-tight mb-4">
                        {harmful ? 'Review Required' : 'Compliant'}
                    </p>

                    {articles && articles.length > 0 && (
                        <div className="space-y-3">
                            <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[#F5F5F7]/30 italic">
                                Referenced CCPA Statutes:
                            </p>
                            <div className="flex flex-wrap gap-2">
                                {articles.map((article, idx) => (
                                    <div
                                        key={idx}
                                        className="flex items-center gap-2 px-3 py-1.5 bg-[#0D0D0D] border border-white/10 text-[10px] font-black uppercase tracking-wider text-[#CBFB45] hover:border-[#CBFB45]/40 transition-colors"
                                    >
                                        <span>{article}</span>
                                        <ExternalLink className="w-3 h-3 text-[#F5F5F7]/30" />
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {referenced_articles && referenced_articles.length > 0 && (
                        <div className="space-y-2 mt-4 pt-4 border-t border-white/10">
                            <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[#F5F5F7]/30 italic">
                                Statute Excerpts:
                            </p>
                            <ul className="text-xs text-[#F5F5F7]/60 space-y-2 list-disc pl-4 italic">
                                {referenced_articles.map((ref, idx) => (
                                    <li key={idx}>{ref}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default VerdictCard;
