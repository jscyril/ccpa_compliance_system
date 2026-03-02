import React from 'react';
import { User, Shield } from 'lucide-react';

const MessageBubble = ({ type, content }) => {
    const isUser = type === 'user';

    return (
        <div className={`flex gap-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
            {!isUser && (
                <div className="w-10 h-10 shrink-0 bg-[#CBFB45] flex items-center justify-center">
                    <Shield className="w-5 h-5 text-[#0D0D0D]" />
                </div>
            )}

            <div className={`max-w-[80%] p-5 text-sm leading-relaxed ${isUser
                    ? 'bg-[#CBFB45] text-[#0D0D0D] font-bold border border-[#CBFB45]'
                    : 'bg-[#1A1A1A] text-[#F5F5F7]/80 border border-white/5'
                }`}>
                {isUser ? (
                    <div className="flex flex-col gap-1">
                        <span className="text-[10px] font-black uppercase tracking-[0.2em] opacity-40 mb-1">USER QUERY</span>
                        {content}
                    </div>
                ) : (
                    <div className="flex flex-col gap-1">
                        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-[#CBFB45] mb-1">AGENT RESPONSE</span>
                        {content}
                    </div>
                )}
            </div>

            {isUser && (
                <div className="w-10 h-10 shrink-0 bg-[#333] flex items-center justify-center">
                    <User className="w-5 h-5 text-white/50" />
                </div>
            )}
        </div>
    );
};

export default MessageBubble;
