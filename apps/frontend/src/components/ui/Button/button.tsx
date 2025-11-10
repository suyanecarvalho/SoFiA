import { ReactNode } from 'react';
import './button.css';

const Button = ({ children }: { children: ReactNode }) => {
    return (
        <button className="buttonStyle">
            {children}
        </button>
    );
};

export default Button;
