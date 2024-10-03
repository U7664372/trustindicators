import React from 'react';
import '../style/Navbar.css';
import UserButton from './UserButton';

// Navbar component

function getSearchBar() {

    const handleSearchClick = () => {
        const searchInput = document.getElementById('search-input').value;
        if (!searchInput) {
            return;
        }
        document.getElementById('search-input').value = '';
        const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(searchInput)}`;
        window.open(searchUrl, '_blank');
    };

    return (
        <div className="search-container">
            <input
                type="text"
                id="search-input"
                placeholder="Search..."/>
            <span className="material-symbols-outlined" onClick={handleSearchClick}>
                search
            </span>
        </div>
    )
}

function getLogo() {
    return (
        <div className="logo">
            <img src="/logo512.png"
                 alt="Trust Indicator Logo"
                 width="70%"
                 height="80%"/>
        </div>
    )
}

function Navbar() {
    const isLoggedIn = true;
    const username = 'JohnDoe';

    return (
        <div className="navigation-bar">
            <div className="top-bar">
                {getLogo()}
                {getSearchBar()}
                {/* user icon */}
                <UserButton isLoggedIn={isLoggedIn} username={username} />
            </div>
        </div>
    );
}

export default Navbar;