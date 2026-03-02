import React from 'react';
import { motion } from 'framer-motion';
import { Search, Brain, ShieldCheck } from 'lucide-react';

const steps = [
    {
        title: "Semantic Retrieval",
        desc: "Large-scale extraction of business practices using vector embeddings and semantic search across CCPA statutes.",
        icon: Search,
        accent: "#CBFB45"
    },
    {
        title: "Legal AI Reasoning",
        desc: "Automated legal analysis using proprietary models trained on California consumer privacy regulations.",
        icon: Brain,
        accent: "#CBFB45"
    },
    {
        title: "Compliance Verdict",
        desc: "Generation of detailed compliance reports with exact citations of Sections 1798.100 through 1798.199.",
        icon: ShieldCheck,
        accent: "#CBFB45"
    }
];

const HowItWorks = () => {
    return (
        <section id="how-it-works" className="py-32 relative bg-[#0D0D0D]">
            <div className="max-w-7xl mx-auto px-6">
                <div className="text-center mb-24">
                    <h2 className="text-sm font-black tracking-[0.4em] text-[#CBFB45] uppercase mb-4">
                        The Pipeline
                    </h2>
                    <h3 className="text-4xl lg:text-6xl font-black text-[#F5F5F7] uppercase tracking-tighter">
                        Engineered for Precision
                    </h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {steps.map((step, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.8, delay: i * 0.2 }}
                            viewport={{ once: true }}
                            className="p-8 bg-[#151515] border border-white/5 relative group"
                        >
                            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-100 transition-opacity">
                                <step.icon className="w-12 h-12 text-[#CBFB45]" strokeWidth={1} />
                            </div>

                            <div className="w-12 h-12 rounded bg-[#CBFB45] flex items-center justify-center mb-8">
                                <step.icon className="w-6 h-6 text-[#0D0D0D]" />
                            </div>

                            <h4 className="text-xl font-black text-[#F5F5F7] uppercase tracking-wide mb-4">
                                {step.title}
                            </h4>

                            <p className="text-[#F5F5F7]/50 text-sm leading-relaxed">
                                {step.desc}
                            </p>

                            <div className="absolute bottom-0 left-0 w-0 h-[2px] bg-[#CBFB45] group-hover:w-full transition-all duration-500" />
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default HowItWorks;
