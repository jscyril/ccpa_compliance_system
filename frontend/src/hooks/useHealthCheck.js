import { useState, useEffect } from 'react';
import { checkHealth } from '../services/api';

const useHealthCheck = () => {
    const [status, setStatus] = useState('checking');

    useEffect(() => {
        const performCheck = async () => {
            try {
                const data = await checkHealth();
                setStatus(data?.status === 'healthy' ? 'healthy' : 'unhealthy');
            } catch {
                // Backend offline — expected when not running
                setStatus('offline');
            }
        };

        performCheck();
        const interval = setInterval(performCheck, 30000);
        return () => clearInterval(interval);
    }, []);

    return status;
};

export default useHealthCheck;
