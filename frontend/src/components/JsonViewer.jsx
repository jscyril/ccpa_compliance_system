import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check, Terminal } from 'lucide-react';
import toast from 'react-hot-toast';

const JsonViewer = ({ data }) => {
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(JSON.stringify(data, null, 2));
        setCopied(true);
        toast.success('Source data copied to clipboard');
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="bg-[#000] border border-white/5 relative group">
            <div className="flex items-center justify-between px-4 py-2 bg-[#1A1A1A] border-b border-white/5">
                <div className="flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-[#CBFB45]" />
                    <span className="text-[10px] font-black uppercase tracking-[0.2em] text-[#F5F5F7]/40">
                        RAW AGENT DATA
                    </span>
                </div>
                <button
                    onClick={handleCopy}
                    className="p-1.5 hover:bg-white/5 text-[#F5F5F7]/30 hover:text-[#CBFB45] transition-all"
                >
                    {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                </button>
            </div>

            <div className="max-h-[300px] overflow-y-auto custom-scrollbar p-1 text-[12px]">
                <SyntaxHighlighter
                    language="json"
                    style={atomDark}
                    customStyle={{
                        margin: 0,
                        padding: '1rem',
                        background: 'transparent',
                        fontSize: '12px',
                        fontFamily: 'JetBrains Mono, monospace',
                    }}
                >
                    {JSON.stringify(data, null, 2)}
                </SyntaxHighlighter>
            </div>
        </div>
    );
};

export default JsonViewer;
