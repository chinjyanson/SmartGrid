import { useEffect } from 'react';

const NotFound = () => {
    useEffect(() => {
        document.title = '404 | Smart Grid';
    }, []);
    return (
        <main className="not-found">
            <h1>404</h1>
            <p>Page not found</p>
        </main>
    )
}

export default NotFound;
