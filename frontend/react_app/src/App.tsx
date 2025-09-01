import React, { useState, useEffect } from 'react';
import './App.css';
import VoiceAssistant from './VoiceAssistant';

function App() {
  const [currentView, setCurrentView] = useState('home');
  const [chatMessage, setChatMessage] = useState('');
  const [chatResponse, setChatResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showLangs, setShowLangs] = useState(false);
  const [servicesOpen, setServicesOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string>("");
  const languages = ['English', 'हिंदी', 'ಕನ್ನಡ', 'தமிழ்', 'తెలుగు', 'మరాఠీ'];
  const [selectedLanguage, setSelectedLanguage] = useState<string>(() => localStorage.getItem('specter_lang') || 'English');

  // Listen for voice assistant navigation events
  useEffect(() => {
    const handleVoiceNavigation = (event: CustomEvent) => {
      const view = event.detail;
      if (view === 'services') {
        setServicesOpen(true);
      } else {
        setCurrentView(view);
      }
    };

    window.addEventListener('navigateTo', handleVoiceNavigation as EventListener);
    return () => {
      window.removeEventListener('navigateTo', handleVoiceNavigation as EventListener);
    };
  }, []);

  const t = (key: string): string => {
    const dict: Record<string, Record<string, string>> = {
      English: { home: 'home', chat: 'chat', upload: 'upload', solutions: 'solutions', contact: 'contact', ask: 'Ask Legal Questions', upload_docs: 'Upload Documents', legal_solutions: 'Legal Solutions', contact_lawyer: 'Contact Lawyer', title: 'SPECTER AI', subtitle: 'Your AI Legal Assistant', translate: 'Translate' },
      'हिंदी': { home: 'होम', chat: 'चैट', upload: 'अपलोड', solutions: 'समाधान', contact: 'संपर्क', ask: 'कानूनी प्रश्न पूछें', upload_docs: 'दस्तावेज़ अपलोड', legal_solutions: 'कानूनी समाधान', contact_lawyer: 'वकील से संपर्क', title: 'SPECTER AI', subtitle: 'आपका एआई कानूनी सहायक', translate: 'अनुवाद करें' },
      'ಕನ್ನಡ': { home: 'ಮುಖಪುಟ', chat: 'ಚಾಟ್', upload: 'ಅಪ್‌ಲೋಡ್', solutions: 'ಪರಿಹಾರ', contact: 'ಸಂಪರ್ಕ', ask: 'ಕಾನೂನು ಪ್ರಶ್ನೆಗಳು ಕೇಳಿ', upload_docs: 'ದಾಖಲೆಗಳನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ', legal_solutions: 'ಕಾನೂನು ಪರಿಹಾರಗಳು', contact_lawyer: 'ವಕೀಲರನ್ನು ಸಂಪರ್ಕಿಸಿ', title: 'SPECTER AI', subtitle: 'ನಿಮ್ಮ ಎಐ ಕಾನೂನು ಸಹಾಯಕ', translate: 'ಅನುವಾದಿಸಿ' },
      'தமிழ்': { home: 'முகப்பு', chat: 'அரட்டை', upload: 'பதிவேற்று', solutions: 'தீர்வுகள்', contact: 'தொடர்பு', ask: 'சட்ட கேள்விகள் கேளுங்கள்', upload_docs: 'ஆவணங்களை பதிவேற்று', legal_solutions: 'சட்ட தீர்வுகள்', contact_lawyer: 'வக்கீலை தொடர்பு கொள்ளவும்', title: 'SPECTER AI', subtitle: 'உங்கள் AI சட்ட உதவியாளர்', translate: 'மொழிபெயர்' },
      'తెలుగు': { home: 'హోమ్', chat: 'చాట్', upload: 'అప్లోడ్', solutions: 'పరిష్కారాలు', contact: 'సంప్రదించండి', ask: 'న్యాయ ప్రశ్నలు అడగండి', upload_docs: 'పత్రాలు అప్లోడ్ చేయండి', legal_solutions: 'న్యాయ పరిష్కారాలు', contact_lawyer: 'న్యాయవాదిని సంప్రదించండి', title: 'SPECTER AI', subtitle: 'మీ AI న్యాయ సహాయకుడు', translate: 'అనువదించు' },
      'మరాఠీ': { home: 'ముఖ్యపృష్ఠ', chat: 'చాట్', upload: 'అప్లోడ్', solutions: 'ఉపాధి', contact: 'సంపర్కించండి', ask: 'కాయదేశీర ప్రశ్న విచారం', upload_docs: 'దస్తావజ్ అప్లోడ్ చేయండి', legal_solutions: 'కాయదేశీర ఉపాధి', contact_lawyer: 'వకిలాశీ సంపర్కించండి', title: 'SPECTER AI', subtitle: 'మీ ఏఆయ విధి సహాయక', translate: 'భాషాంతర' },
    };
    const pack = dict[selectedLanguage] || dict.English;
    return pack[key] || key;
  };

  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatMessage.trim()) return;
    
    setIsLoading(true);
    try {
      const prefixed = selectedLanguage === 'English' ? chatMessage : `Respond in ${selectedLanguage}. ${chatMessage}`;
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: prefixed })
      });
      const data = await response.json();
      setChatResponse(data.answer);
    } catch (error) {
             setChatResponse('Error connecting to SPECTER. Please try again.');
    }
    setIsLoading(false);
  };

  const handleTranslate = async () => {
    if (!chatResponse.trim() || selectedLanguage === 'English') return;
    try {
      const resp = await fetch('http://localhost:8000/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: chatResponse, target_lang: selectedLanguage })
      });
      const data = await resp.json();
      if (data.translated) setChatResponse(data.translated);
    } catch(e) {}
  };

  const renderContent = () => {
    switch (currentView) {
      case 'chat':
        return (
          <div className="bot-interface">
                         <h2>Ask SPECTER</h2>
            <form onSubmit={handleChatSubmit} className="chat-form">
              <textarea
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                placeholder="Ask your legal question..."
                className="chat-input"
              />
              <button type="submit" disabled={isLoading} className="chat-btn">
                {isLoading ? 'Thinking...' : 'Ask'}
              </button>
            </form>
                         {chatResponse && (
              <div className="chat-response">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h3>SPECTER Response:</h3>
                  {selectedLanguage !== 'English' && (
                    <button className="chat-btn" onClick={handleTranslate} style={{ padding: '8px 12px', fontSize: 12 }}>
                      {t('translate')}
                    </button>
                  )}
                </div>
                <FormattedResponse text={chatResponse} />
              </div>
            )}
            <button onClick={() => setCurrentView('home')} className="back-btn">
              ← Back to Home
            </button>
          </div>
        );
      
      case 'upload':
        return (
          <div className="bot-interface">
            <h2>Upload Legal Documents</h2>
            <p>Upload your legal documents for analysis</p>
            <input
              type="file"
              className="file-input"
              onChange={(e) => {
                const f = e.target.files && e.target.files[0] ? e.target.files[0] : null;
                setSelectedFile(f);
                setUploadStatus("");
              }}
            />
            <button
              className="upload-btn"
              onClick={async () => {
                if (!selectedFile) {
                  setUploadStatus("Select a file first.");
                  return;
                }
                try {
                  const form = new FormData();
                  form.append('file', selectedFile);
                  const resp = await fetch('http://localhost:8000/upload', {
                    method: 'POST',
                    body: form
                  });
                  const data = await resp.json();
                  if (resp.ok) {
                    setUploadStatus(`Uploaded: ${data.filename}`);
                  } else {
                    setUploadStatus(`Upload failed: ${data.message || 'server error'}`);
                  }
                } catch (e) {
                  setUploadStatus('Upload failed. Check backend is running.');
                }
              }}
            >
              Upload
            </button>
            {uploadStatus && <p style={{ marginTop: 8 }}>{uploadStatus}</p>}
            <button onClick={() => setCurrentView('home')} className="back-btn">
              ← Back to Home
            </button>
          </div>
        );
      
      case 'solutions':
        return (
          <div className="bot-interface">
            <h2>Legal Solutions</h2>
            <p>Get detailed legal solutions for your problems</p>
            <form className="solutions-form" onSubmit={(e) => e.preventDefault()}>
              <textarea placeholder="Describe your legal problem..." className="solutions-input" />
              <button className="solutions-btn" type="submit">Get Solutions</button>
            </form>
            <button onClick={() => setCurrentView('home')} className="back-btn">
              ← Back to Home
            </button>
          </div>
        );
      
      case 'contact':
        return (
          <div className="bot-interface">
            <h2>Contact Human Lawyer</h2>
            <p>Connect with a real lawyer for consultation</p>
            <form className="contact-form">
              <input type="text" placeholder="Your Name" />
              <input type="email" placeholder="Your Email" />
              <textarea placeholder="Describe your case..." />
              <button type="submit" className="contact-btn">Send Request</button>
            </form>
            <button onClick={() => setCurrentView('home')} className="back-btn">
              ← Back to Home
            </button>
          </div>
        );
      
      default:
        return (
          <div className="main-content" style={{ position: 'relative', zIndex: 1 }}>
            <div className="central-greeting">
              <h1 className="hello-text">SPECTER.</h1>
              <p className="subtitle">{t('subtitle')}</p>
            </div>
            
            <div className="feature-grid">
              <button onClick={() => setCurrentView('chat')} className="feature-btn">
                <span className="feature-icon">💬</span>
                <span className="feature-text">{t('ask')}</span>
              </button>
              
              <button onClick={() => setCurrentView('upload')} className="feature-btn">
                <span className="feature-icon">📄</span>
                <span className="feature-text">{t('upload_docs')}</span>
              </button>
              
              
              <button onClick={() => setCurrentView('solutions')} className="feature-btn">
                <span className="feature-icon">⚖️</span>
                <span className="feature-text">{t('legal_solutions')}</span>
              </button>
              
              <button onClick={() => setServicesOpen(true)} className="feature-btn">
                <span className="feature-icon">🏛️</span>
                <span className="feature-text">Legal Services</span>
              </button>

              <button onClick={() => setCurrentView('contact')} className="feature-btn">
                <span className="feature-icon">👨‍💼</span>
                <span className="feature-text">{t('contact_lawyer')}</span>
              </button>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="app-container">
      {/* Top Navigation */}
      <nav className="top-nav">
        <div className="nav-left">
          <button className="hamburger" aria-label="menu" onClick={() => setSidebarOpen(s => !s)}>
            <span />
            <span />
            <span />
          </button>
          <div className="logo">
            <div>LAW</div>
            <div>BOT</div>
            <div>AI</div>
          </div>
        </div>
        
                 <div className="nav-center">
           <span className="nav-title">{t('title')}</span>
         </div>
        
        <div className="nav-right">
          <div className="lang-selector">
            <button className="lang-button" onClick={() => setShowLangs(v => !v)}>
              {selectedLanguage}
            </button>
            {showLangs && (
              <div className="lang-dropdown">
                {languages.map((lang) => (
                  <div key={lang} className={`lang-item ${lang === selectedLanguage ? 'active' : ''}`} onClick={() => { setSelectedLanguage(lang); localStorage.setItem('specter_lang', lang); setShowLangs(false); }}>
                    {lang}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* Slide-out Sidebar */}
      <nav className={`side-nav ${sidebarOpen ? 'open' : ''}`}>
        <ul>
          <li className={currentView === 'home' ? 'active' : ''} onClick={() => { setCurrentView('home'); setSidebarOpen(false); }}>
            {t('home')}
          </li>
          <li onClick={() => { setCurrentView('chat'); setSidebarOpen(false); }}>{t('chat')}</li>
          <li onClick={() => { setCurrentView('upload'); setSidebarOpen(false); }}>{t('upload')}</li>
          
          <li onClick={() => { setCurrentView('solutions'); setSidebarOpen(false); }}>{t('solutions')}</li>
          <li onClick={() => { setCurrentView('contact'); setSidebarOpen(false); }}>{t('contact')}</li>
        </ul>
      </nav>
      {sidebarOpen && <div className="backdrop" onClick={() => setSidebarOpen(false)} />}
      <LegalServicesPanel isOpen={servicesOpen} onClose={() => setServicesOpen(false)} />

      {/* Main Content */}
      <main className="main-area">
        {renderContent()}
      </main>

      {/* Bottom Left Scroll Indicator */}
      <div className="scroll-indicator">
        <span>scroll down</span>
        <div className="scroll-line"></div>
      </div>

      {/* Voice Assistant */}
      <VoiceAssistant />
    </div>
  );
}

export default App;

export function FormattedResponse({ text }: { text: string }) {
  const lines = text.split('\n');
  const elements: React.ReactNode[] = [];
  let listOpen = false;
  let listItems: React.ReactNode[] = [];

  const flushList = () => {
    if (listOpen && listItems.length) {
      elements.push(<ul className="resp-list" style={{ marginTop: 6, marginBottom: 6, paddingLeft: 18 }}>{listItems}</ul>);
    }
    listOpen = false;
    listItems = [];
  };

  lines.forEach((raw, idx) => {
    const line = raw.trim();
    if (!line) {
      flushList();
      elements.push(<div key={`sp-${idx}`} style={{ height: 6 }} />);
      return;
    }
    if (line.startsWith('- ')) {
      listOpen = true;
      listItems.push(<li key={`li-${idx}`}>{line.slice(2)}</li>);
      return;
    }
    flushList();
    const labels = ['Answer', 'Legal Reference', 'Explanation', 'Next Steps'];
    const matched = labels.find(l => line.startsWith(l + ':'));
    if (matched) {
      const value = line.slice(matched.length + 1).trim();
      if (matched === 'Next Steps') {
        elements.push(<div key={`hd-${idx}`} className="resp-line" style={{ fontWeight: 700, marginTop: 4 }}>{matched}:</div>);
      } else {
        elements.push(
          <div key={`ln-${idx}`} className="resp-line" style={{ marginBottom: 4 }}>
            <span style={{ fontWeight: 700 }}>{matched}:</span> {value}
          </div>
        );
      }
    } else {
      elements.push(<div key={`tx-${idx}`} className="resp-line" style={{ whiteSpace: 'pre-line' }}>{line}</div>);
    }
  });
  flushList();
  return <div className="formatted-response" style={{ lineHeight: 1.55 }}>{elements}</div>;
}

export function LegalServicesPanel({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const services = [
    { name: 'Bar Council of India', url: 'http://www.barcouncilofindia.org', category: 'Regulation' },
    { name: 'Department of Justice', url: 'https://doj.gov.in/', category: 'Judicial' },
    { name: 'India.gov.in – Legal Aid', url: 'https://www.india.gov.in/topics/law-justice/legal-aid', category: 'Legal Aid' },
    { name: 'Law Commission of India', url: 'https://lawcommissionofindia.nic.in/', category: 'Research' },
    { name: 'Ministry of Law and Justice', url: 'https://www.india.gov.in/ministry-law-justice', category: 'Central' },
    { name: 'NALSA (National Legal Services Authority)', url: 'https://nalsa.gov.in/', category: 'Legal Aid' },
    { name: 'National Judicial Reference System (NJRS)', url: 'https://ecourts.gov.in/', category: 'Courts' },
    { name: 'National Portal of India', url: 'http://india.gov.in', category: 'E‑Governance' },
    { name: 'NHAI', url: 'https://nhai.gov.in/', category: 'Transport' },
    { name: 'Parivahan', url: 'https://parivahan.gov.in/', category: 'Transport' },
    { name: 'SC Legal Services Committee (SCLSC)', url: 'https://sclsc.gov.in/', category: 'Legal Aid' },
    { name: 'Shram Suvidha', url: 'https://shramsuvidha.gov.in', category: 'Labour' },
    { name: 'Udyam Registration', url: 'https://udyamregistration.gov.in', category: 'MSME' },
    { name: 'Virtual Courts (e‑Courts)', url: 'https://vcourts.gov.in/', category: 'Courts' },
  ].sort((a, b) => a.name.localeCompare(b.name));

  if (!isOpen) return null;
  return (
    <div className="backdrop" onClick={onClose}>
      <div
        className="bot-interface"
        style={{ maxWidth: 800, margin: '80px auto', background: 'rgba(17,17,17,0.95)' }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2>Legal Registration & Online Services</h2>
        <div style={{ maxHeight: 420, overflowY: 'auto', textAlign: 'left' }}>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {services.map((s) => (
              <li key={s.name} style={{ padding: '10px 6px', borderBottom: '1px solid #333' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: 700 }}>{s.name}</div>
                    <div style={{ opacity: 0.8, fontSize: 12 }}>{s.category}</div>
                  </div>
                  <a href={s.url} target="_blank" rel="noopener noreferrer" className="chat-btn" style={{ padding: '8px 12px' }}>
                    Open
                  </a>
                </div>
              </li>
            ))}
          </ul>
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 12 }}>
          <button className="back-btn" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}
