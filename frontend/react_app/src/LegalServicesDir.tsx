import React from 'react';
import './LegalServices.css';
import { legalServicesData } from './LegalServicesData';

const LegalServicesDir: React.FC = () => {
    const scrollToSection = (id: string) => {
        const element = document.getElementById(id);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    };

    return (
        <div className="legal-services-container">
            <div className="services-sidebar">
                <h4 style={{ padding: '0 10px', color: '#666', marginBottom: '10px' }}>Index</h4>
                {Object.keys(legalServicesData).map((key) => (
                    <button
                        key={key}
                        onClick={() => scrollToSection(key)}
                        className="sidebar-link"
                    >
                        {key}
                    </button>
                ))}
            </div>

            <div className="services-content">
                <h2>Legal Registration & Online Services</h2>
                <p className="subtitle">Comprehensive directory of Indian Government & Legal Portals</p>

                {Object.entries(legalServicesData).map(([category, links]) => (
                    <div key={category} id={category} className="service-section">
                        <h3 className="section-title">{category}</h3>
                        <div className="links-grid">
                            {links.map((link, index) => (
                                <a
                                    key={index}
                                    href={`https://${link.split(' ')[0]}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="service-link"
                                >
                                    {link}
                                </a>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default LegalServicesDir;
