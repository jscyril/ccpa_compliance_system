import React from 'react';
import { Toaster } from 'react-hot-toast';
import Home from './pages/Home';

function App() {
    return (
        <>
            <Home />
            <Toaster
                position="bottom-right"
                toastOptions={{
                    style: {
                        background: '#1A1A1A',
                        color: '#F5F5F7',
                        border: '1px solid rgba(203, 251, 69, 0.2)',
                        borderRadius: '0px',
                        fontSize: '10px',
                        textTransform: 'uppercase',
                        letterSpacing: '0.1em',
                        fontWeight: '900',
                    },
                }}
            />
        </>
    );
}

export default App;
