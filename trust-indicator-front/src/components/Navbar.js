import React, { useState } from 'react';
import '../style/Navbar.css';
import UserButton from './UserButton';

// Top Navigation Bar

function Navbar() {
    const [language, setLanguage] = useState('EN');

    const [isDropdownVisible, setDropdownVisible] = useState(false);


    const signIn = () => {
        console.log("Sign in clicked");
    };

    const signOut = (event) => {
        event.stopPropagation();
        console.log("Sign out clicked");
    };

    const toggleDropdown = (event) => {
        event.stopPropagation();
        setDropdownVisible(!isDropdownVisible);
    };

    const updateLanguage = (newLanguage, event) => {
        event.stopPropagation();
        setLanguage(newLanguage);
    };

    //
    // Search
    //
    const [query, setQuery] = useState('');

    const handleInputChange = (e) => {
        setQuery(e.target.value);
    };

    const handleSearch = () => {
        console.log('Searching for:', query);
        setQuery('')
    };

    //
    // User Icon Pressed
    //

    return (
        <div className="navigation-bar">
            <div className="top-bar">

                {/* search */}
                <div className="search-container">
                    <input
                        type="text"
                        id="search-input"
                        placeholder="Search..."
                        value={query}
                        onChange={handleInputChange}
                    />
                    <button
                        type="button"
                        id="search-button"
                        onClick={handleSearch}
                    >
                         {/* or you can use an icon */}
                    </button>
                </div>

                <UserButton />
                {/* user */}
                {/*<div className="user-container" tabIndex="0">*/}
                {/*    <UserButton />*/}
                {/*</div>*/}
                {/*<div className="user-container" tabIndex="0">*/}
                {/*    <UserButton />*/}
                {/*</div>*/}
            </div>

            <div className="bottom-bar"> {/* Fixed the typo */}
                {/* Additional content for bottom-bar can go here */}
            </div>

            <div className="logo">
                <img src="/logo512.png"
                     alt="Trust Indicator Logo"
                     width="70%"
                     height="80%"/>
            </div>
        </div>
    );
}

export default Navbar;