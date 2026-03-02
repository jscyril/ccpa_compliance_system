import React from 'react';
import { motion } from 'framer-motion';

const MeshBackground = () => {
    return (
        <div className="fixed inset-0 -z-10 bg-[#0D0D0D] overflow-hidden">
            {/* Pulsr Grid Overlay */}
            <div className="absolute inset-0 grid-overlay opacity-20" />

            {/* Pulsr Deep Navy Glows (Vignette style) */}
            <motion.div
                animate={{
                    opacity: [0.4, 0.6, 0.4],
                    scale: [1, 1.1, 1],
                }}
                transition={{
                    duration: 15,
                    repeat: Infinity,
                    ease: "easeInOut",
                }}
                className="absolute top-[-20%] left-[-20%] w-[140%] h-[140%] rounded-full"
                style={{
                    background: 'radial-gradient(circle at center, #001833 0%, transparent 60%)',
                    filter: 'blur(150px)',
                }}
            />

            {/* Neon Lime Accent Glow (Bottom Right) */}
            <motion.div
                animate={{
                    x: [0, -30, 0],
                    y: [0, -20, 0],
                    opacity: [0.1, 0.15, 0.1],
                }}
                transition={{
                    duration: 10,
                    repeat: Infinity,
                    ease: "easeInOut",
                }}
                className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[60%] rounded-full"
                style={{
                    background: 'radial-gradient(circle at center, #CBFB45 0%, transparent 70%)',
                    filter: 'blur(100px)',
                }}
            />

            {/* Minimal Pulsr Particles (Technical Dots) */}
            {[...Array(15)].map((_, i) => (
                <motion.div
                    key={i}
                    initial={{
                        x: Math.random() * 100 + '%',
                        y: Math.random() * 100 + '%',
                    }}
                    animate={{
                        opacity: [0, 0.3, 0],
                        scale: [0, 1, 0],
                    }}
                    transition={{
                        duration: Math.random() * 5 + 3,
                        repeat: Infinity,
                        ease: "easeInOut",
                        delay: Math.random() * 5,
                    }}
                    className="absolute w-[2px] h-[2px] bg-[#CBFB45] rounded-full pointer-events-none"
                />
            ))}
        </div>
    );
};

export default MeshBackground;
