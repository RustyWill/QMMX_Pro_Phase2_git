// src/components/QBrandHeader.js
import React from 'react';
import bg from '../assets/header-bg.jpg';       // ← import the image
import './QBrandHeader.css';

export default function QBrandHeader() {
  return (
    <header className="qmmx-header">
      <div
        className="qmmx-header-bg"
        style={{ backgroundImage: `url(${bg})` }}  // ← use it here
      />
      <div className="qmmx-header-content">
        <img src="/qmmx-icon.png" alt="QMMX Icon" className="qmmx-header-icon" />
        <h1 className="qmmx-header-title">QMMX Pro</h1>
      </div>
    </header>
  );
}

