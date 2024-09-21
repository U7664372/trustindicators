import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const UserButton = () => {
    const { isLoggedIn } = useAuth();
    const navigate = useNavigate();

    const handleClick = () => {
        if (isLoggedIn) {
            navigate('/profile');
        } else {
            navigate('/login');
        }
    };

    return (
        <div className="user-container" onClick={handleClick}>
            <i className="fa fa-user" style={{ fontSize: '24px' }}></i>
        </div>
    );
};

export default UserButton;
