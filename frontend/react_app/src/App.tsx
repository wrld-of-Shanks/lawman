import React, { useState, useEffect } from 'react';
import './App.css';
import VoiceAssistant from './VoiceAssistant.js';
import config from './config.ts';
import './LegalServices.css';
import { legalServicesData } from './LegalServicesData';

function App() {
  const [currentView, setCurrentView] = useState('home');
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{ message: string, response: string, isSolution: boolean }>>([]);

  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showLangs, setShowLangs] = useState(false);
  const [servicesOpen, setServicesOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string>("");
  const [extractedText, setExtractedText] = useState('');
  const [docType, setDocType] = useState('');
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [selectedAction, setSelectedAction] = useState('summarize');

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
    const userMessage = chatMessage;

    try {
      const prefixed = selectedLanguage === 'English' ? userMessage : `Respond in ${selectedLanguage}. ${userMessage}`;
      const response = await fetch(`${config.API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: prefixed })
      });
      const data = await response.json();

      setChatHistory(prev => [{
        message: userMessage,
        response: data.answer || 'No response generated.',
        isSolution: false
      }, ...prev]);
    } catch (error) {
      setChatHistory(prev => [{
        message: userMessage,
        response: 'Error connecting to SPECTER. Please try again.',
        isSolution: false
      }, ...prev]);
    }
    setIsLoading(false);
  };



  const handleAnalyze = async (action: string) => {
    setIsLoading(true);
    try {
      const resp = await fetch(`${config.API_BASE_URL}/analyze_doc`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: extractedText,
          doc_type: docType,
          action: action,
          target_lang: selectedLanguage
        })
      });
      const data = await resp.json();
      setAnalysisResult({ ...data, type: action });
    } catch (e) {
      alert("Analysis failed. Please try again.");
    }
    setIsLoading(false);
  };

  const renderAnalysisResult = () => {
    if (!analysisResult) return null;

    if (analysisResult.type === 'summarize') {
      return (
        <div className="summary-view">
          <FormattedResponse text={analysisResult.summary} />
        </div>
      );
    }
    if (analysisResult.type === 'translate') {
      return (
        <div className="translation-view">
          <FormattedResponse text={analysisResult.translation} />
        </div>
      );
    }
    if (analysisResult.type === 'verify') {
      return (
        <div className="verification-view">
          <div className={`verdict-badge ${analysisResult.verdict.includes('correct') ? 'success' : 'warning'}`}>
            {analysisResult.verdict}
          </div>
          <FormattedResponse text={analysisResult.full_analysis} />
        </div>
      );
    }
  };

  const deleteMessage = (index: number) => {
    setChatHistory(prev => prev.filter((_, i) => i !== index));
  };

  const renderContent = () => {
    switch (currentView) {
      case 'chat':
        return (
          <div className="bot-interface">
            <h2>SPECTER - AI Legal Assistant</h2>
            <div className="chat-interface">
              <form onSubmit={handleChatSubmit} className="chat-form">
                <div className="input-wrapper">
                  <textarea
                    value={chatMessage}
                    onChange={(e) => setChatMessage(e.target.value)}
                    placeholder="Ask your legal question..."
                    className="chat-input"
                    rows={3}
                  />
                  {chatMessage && (
                    <button
                      type="button"
                      className="clear-btn"
                      onClick={() => setChatMessage('')}
                      aria-label="Clear question"
                    >
                      ×
                    </button>
                  )}
                </div>
                <button type="submit" disabled={isLoading} className="chat-btn">
                  {isLoading ? 'Thinking...' : 'Ask'}
                </button>
              </form>

              <div className="chat-history">
                {chatHistory.map((item, index) => (
                  <div key={index} className="chat-message">
                    <div className="message-header">
                      <strong>You:</strong>
                      <button
                        onClick={() => deleteMessage(index)}
                        className="delete-btn"
                        title="Delete message"
                      >
                        ×
                      </button>
                    </div>
                    <div className="user-message">{item.message}</div>
                    <div className="message-header">
                      <strong>SPECTER Response:</strong>
                    </div>
                    <div className="assistant-response">
                      <FormattedResponse text={item.response} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <button onClick={() => setCurrentView('home')} className="back-btn">
              ← Back to Home
            </button>
          </div>
        );

      case 'upload':
        return (
          <div className="bot-interface">
            <h2>{t('upload_docs')}</h2>

            {!extractedText ? (
              <div className="upload-section">
                <div className="action-selector-container">
                  <p className="selector-label">Choose Analysis Type:</p>
                  <div className="action-selector">
                    <label className={`action-option ${selectedAction === 'summarize' ? 'active' : ''}`}>
                      <input
                        type="radio"
                        name="action"
                        value="summarize"
                        checked={selectedAction === 'summarize'}
                        onChange={() => setSelectedAction('summarize')}
                      />
                      <span className="option-icon">📝</span> Summarize
                    </label>
                    <label className={`action-option ${selectedAction === 'translate' ? 'active' : ''}`}>
                      <input
                        type="radio"
                        name="action"
                        value="translate"
                        checked={selectedAction === 'translate'}
                        onChange={() => setSelectedAction('translate')}
                      />
                      <span className="option-icon">🌐</span> Translate
                    </label>
                    <label className={`action-option ${selectedAction === 'verify' ? 'active' : ''}`}>
                      <input
                        type="radio"
                        name="action"
                        value="verify"
                        checked={selectedAction === 'verify'}
                        onChange={() => setSelectedAction('verify')}
                      />
                      <span className="option-icon">⚖️</span> Verify
                    </label>
                  </div>
                </div>

                <div className="file-upload-wrapper">
                  <input
                    type="file"
                    id="file-upload"
                    className="file-input"
                    accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
                    onChange={(e) => {
                      const f = e.target.files && e.target.files[0] ? e.target.files[0] : null;
                      setSelectedFile(f);
                      setUploadStatus("");
                    }}
                  />
                </div>

                <button
                  className="upload-btn"
                  disabled={isLoading}
                  onClick={async () => {
                    if (!selectedFile) {
                      setUploadStatus("Select a file first.");
                      return;
                    }
                    setIsLoading(true);
                    try {
                      // Step 1: Upload
                      const form = new FormData();
                      form.append('file', selectedFile);
                      const resp = await fetch(`${config.API_BASE_URL}/upload_doc`, {
                        method: 'POST',
                        body: form
                      });
                      const data = await resp.json();

                      if (resp.ok) {
                        setExtractedText(data.text);
                        setDocType(data.doc_type);

                        // Step 2: Analyze immediately
                        const analyzeResp = await fetch(`${config.API_BASE_URL}/analyze_doc`, {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({
                            text: data.text,
                            doc_type: data.doc_type,
                            action: selectedAction,
                            target_lang: selectedLanguage
                          })
                        });
                        const analyzeData = await analyzeResp.json();
                        setAnalysisResult({ ...analyzeData, type: selectedAction });
                        setUploadStatus("Analysis complete!");
                      } else {
                        setUploadStatus(`Upload failed: ${data.detail || 'server error'}`);
                      }
                    } catch (e) {
                      setUploadStatus('Process failed. Check backend connection.');
                    }
                    setIsLoading(false);
                  }}
                >
                  {isLoading ? 'Processing...' : `Upload & ${selectedAction.charAt(0).toUpperCase() + selectedAction.slice(1)}`}
                </button>
                {uploadStatus && <p className="status-msg">{uploadStatus}</p>}
              </div>
            ) : (
              <div className="analysis-section">
                <div className="doc-info-card">
                  <h3>📄 Document Detected: {docType}</h3>
                  <button className="reset-btn" onClick={() => {
                    setExtractedText('');
                    setAnalysisResult(null);
                    setUploadStatus('');
                    setSelectedFile(null);
                  }}>Upload New File</button>
                </div>

                {!analysisResult ? (
                  <div className="action-grid">
                    <button className="action-card" onClick={() => handleAnalyze('summarize')}>
                      <span className="icon">📝</span>
                      <h4>Summarize</h4>
                      <p>Get a concise legal summary</p>
                    </button>
                    <button className="action-card" onClick={() => handleAnalyze('translate')}>
                      <span className="icon">🌐</span>
                      <h4>Translate</h4>
                      <p>Translate to local language</p>
                    </button>
                    <button className="action-card" onClick={() => handleAnalyze('verify')}>
                      <span className="icon">⚖️</span>
                      <h4>Verify Legality</h4>
                      <p>Check for legal compliance</p>
                    </button>
                  </div>
                ) : (
                  <div className="result-card">
                    <div className="result-header">
                      <h3>Analysis Result</h3>
                      <button className="back-btn-small" onClick={() => setAnalysisResult(null)}>← Back</button>
                    </div>
                    <div className="result-content">
                      {renderAnalysisResult()}
                    </div>
                    <div className="result-actions">
                      <button className="copy-btn" onClick={() => navigator.clipboard.writeText(JSON.stringify(analysisResult, null, 2))}>
                        Copy Result
                      </button>
                    </div>
                  </div>
                )}

                {isLoading && <div className="loading-overlay">AI is analyzing your document...</div>}
              </div>
            )}

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
              <button onClick={() => setCurrentView('chat')} className="feature-btn main-btn">
                <span className="feature-icon">🤖</span>
                <span className="feature-text">SPECTER</span>
              </button>

              <button onClick={() => setCurrentView('upload')} className="feature-btn main-btn">
                <span className="feature-icon">📄</span>
                <span className="feature-text">{t('upload_docs')}</span>
              </button>

              <button onClick={() => setServicesOpen(true)} className="feature-btn main-btn">
                <span className="feature-icon">🏛️</span>
                <span className="feature-text">Legal Services</span>
              </button>

              <button onClick={() => setCurrentView('contact')} className="feature-btn main-btn">
                <span className="feature-icon">👨‍⚖️</span>
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
          <button className="subscription-btn">
            Subscription
          </button>
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
        <div className="sidebar-main">
          <ul className="sidebar-nav-links">
            <li className={currentView === 'home' ? 'active' : ''} onClick={() => { setCurrentView('home'); setSidebarOpen(false); }}>
              {t('home')}
            </li>
            <li onClick={() => { setCurrentView('chat'); setSidebarOpen(false); }}>SPECTER</li>
            <li onClick={() => { setCurrentView('upload'); setSidebarOpen(false); }}>{t('upload')}</li>
            <li onClick={() => { setServicesOpen(true); setSidebarOpen(false); }}>Legal Services</li>
            <li onClick={() => { setCurrentView('contact'); setSidebarOpen(false); }}>{t('contact')}</li>
          </ul>
        </div>
        <div className="sidebar-footer">
          <ul className="footer-links">
            <li><a href="/privacy-policy.html" target="_blank">Privacy Policy</a></li>
            <li><a href="/terms-conditions.html" target="_blank">Terms & Conditions</a></li>
            <li><a href="/refund-policy.html" target="_blank">Refund Policy</a></li>
            <li><a href="/shipping-policy.html" target="_blank">Shipping Policy</a></li>
            <li><a href="/contact.html" target="_blank">Contact Us</a></li>
          </ul>
        </div>
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
  if (!isOpen) return null;
  return (
    <div className="backdrop" onClick={onClose}>
      <div
        className="bot-interface"
        style={{
          maxWidth: '95vw',
          width: '1400px',
          height: '90vh',
          margin: '40px auto',
          background: 'rgba(17,17,17,0.95)',
          padding: 0,
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ padding: '15px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#111', borderBottom: '1px solid #333' }}>
          <h2 style={{ margin: 0, fontSize: '1.2rem', color: '#fbbf24' }}>Legal Services Directory</h2>
          <button onClick={onClose} className="chat-btn" style={{ background: '#333', padding: '8px 16px' }}>Close</button>
        </div>
        <div style={{ flex: 1, overflow: 'hidden' }}>
          <div className="legal-services-container">
            <div className="services-sidebar">
              <h4 style={{ padding: '0 10px', color: '#666', marginBottom: '10px' }}>Index</h4>
              {Object.keys(legalServicesData).map((key) => (
                <button
                  key={key}
                  onClick={() => {
                    const element = document.getElementById(key);
                    if (element) {
                      element.scrollIntoView({ behavior: 'smooth' });
                    }
                  }}
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
        </div>
      </div>
    </div>
  );
}
