import React from 'react';
import '../style/UserButton.css';

function LoginForm() {
    const handleLoginClick = () => {
        console.log('Login clicked');
    };

    return (
        <div className="login-form">
            <button className="login-button" onClick={handleLoginClick}>
                <span className="material-symbols-rounded">
                    person
                </span>
            </button>
        </div>
    );
}

function AdminPanel() {

}

function UserButton({isLoggedIn, username}) {
    isLoggedIn = false;
    return (
        <div>
            {isLoggedIn ? <AdminPanel/> : <LoginForm/>}
        </div>
    );
}

export default UserButton;