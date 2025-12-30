import React, { useState, useEffect } from 'react';
import './App.css';
import VoiceAssistant from './VoiceAssistant.js';
import config from './config.ts';
import './LegalServices.css';
import Login from './Login.tsx';
import Signup from './Signup.tsx';
import UserProfile from './UserProfile.tsx';
import { legalServicesData } from './LegalServicesData';

function App() {
  const [currentView, setCurrentView] = useState('login'); // Start at login
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
  const [budgetValue, setBudgetValue] = useState(50000); // Default ₹50,000
  const [requestSent, setRequestSent] = useState(false);

  // Auth State
  const [user, setUser] = useState<any>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('specter_token'));
  const [usageStats, setUsageStats] = useState<any>(null);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);

  const fetchUsageStats = async (authToken: string) => {
    try {
      const response = await fetch(`${config.API_BASE_URL}/usage`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setUsageStats(data);

        // Check if user has exceeded limits
        const questionsExceeded = data.questions.limit !== -1 && data.questions.remaining <= 0;
        const uploadsExceeded = data.uploads.limit !== -1 && data.uploads.remaining <= 0;

        if (questionsExceeded || uploadsExceeded) {
          setShowUpgradeModal(true);
        }
      }
    } catch (error) {
      console.error("Failed to fetch usage stats", error);
    }
  };

  const languages = ['English', 'हिंदी', 'ಕನ್ನಡ', 'தமிழ்', 'తెలుగు', 'మరాಠೀ'];
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

  // Check for existing session
  useEffect(() => {
    if (token) {
      fetch(`${config.API_BASE_URL}/auth/profile`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(res => {
          if (res.ok) return res.json();
          throw new Error('Session expired');
        })
        .then(userData => {
          setUser(userData);
          setCurrentView('home'); // Go to home if logged in
          fetchUsageStats(token); // Fetch usage stats
        })
        .catch(() => {
          handleLogout();
        });
    }
  }, [token]);

  const handleLoginSuccess = (newToken: string, userData: any) => {
    setToken(newToken);
    setUser(userData);
    localStorage.setItem('specter_token', newToken);
    setCurrentView('home');
    fetchUsageStats(newToken); // Fetch usage stats on login
  };

  const handleLogout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('specter_token');
    setCurrentView('login');
  };

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
      const headers: any = { 'Content-Type': 'application/json' };

      // Add auth token if user is logged in
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${config.API_BASE_URL}/chat`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ message: prefixed })
      });

      const data = await response.json();

      if (!response.ok) {
        // Handle limit errors
        if (response.status === 403) {
          setChatHistory(prev => [{
            message: userMessage,
            response: `⚠️ ${data.error || 'Usage limit reached. Please upgrade your subscription.'}`,
            isSolution: false
          }, ...prev]);
        } else if (response.status === 401) {
          setChatHistory(prev => [{
            message: userMessage,
            response: '🔒 Please login to use SPECTER.',
            isSolution: false
          }, ...prev]);
        } else {
          throw new Error(data.error || 'Request failed');
        }
      } else {
        setChatHistory(prev => [{
          message: userMessage,
          response: data.answer || 'No response generated.',
          isSolution: false
        }, ...prev]);

        // Refresh usage stats after successful question
        if (token) {
          fetchUsageStats(token);
        }
      }
    } catch (error) {
      setChatHistory(prev => [{
        message: userMessage,
        response: 'Error connecting to SPECTER. Please try again.',
        isSolution: false
      }, ...prev]);
    }
    setIsLoading(false);
    setChatMessage('');
  };



  const handleAnalyze = async (action: string) => {
    setIsLoading(true);
    try {
      const headers: any = { 'Content-Type': 'application/json' };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const resp = await fetch(`${config.API_BASE_URL}/legal/analyze_doc`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          text: extractedText,
          doc_type: docType,
          action: action,
          target_lang: selectedLanguage
        })
      });

      if (resp.status === 401) {
        handleLogout();
        alert("Session expired. Please login again.");
        return;
      }

      const data = await resp.json();
      if (resp.ok) {
        setAnalysisResult({ ...data, type: action });
      } else {
        alert(`Analysis failed: ${data.error || data.detail || 'Unknown error'}`);
      }
    } catch (e) {
      alert("Analysis failed. Please try again.");
    }
    setIsLoading(false);
  };

  const handleDownload = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const renderAnalysisResult = () => {
    if (!analysisResult) return null;

    if (analysisResult.type === 'summarize') {
      return (
        <div className="summary-view" style={{ animation: 'fadeIn 0.5s ease-out' }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px',
            borderBottom: '1px solid #333',
            paddingBottom: '10px'
          }}>
            <h3 style={{ margin: 0, color: '#fbbf24' }}>📝 Document Summary Preview</h3>
            <span style={{ fontSize: '0.8rem', color: '#888' }}>Read below before downloading</span>
          </div>

          <div className="summary-content-box" style={{
            background: '#111',
            padding: '25px',
            borderRadius: '12px',
            border: '1px solid #333',
            marginBottom: '20px',
            maxHeight: '600px',
            overflowY: 'auto',
            lineHeight: '1.6'
          }}>
            <FormattedResponse text={analysisResult.summary} />
          </div>

          <div style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
            <button
              className="download-btn"
              onClick={() => handleDownload(analysisResult.summary, `Summary_${docType.replace(/\s+/g, '_')}.txt`)}
              style={{
                background: '#fbbf24',
                color: '#000',
                border: 'none',
                padding: '12px 24px',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: 'bold',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                fontSize: '1rem',
                boxShadow: '0 4px 12px rgba(251, 191, 36, 0.2)',
                transition: 'transform 0.2s, box-shadow 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 6px 16px rgba(251, 191, 36, 0.3)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(251, 191, 36, 0.2)';
              }}
            >
              <span>📥</span> Download Complete Summary (.txt)
            </button>
          </div>
        </div>
      );
    }
    if (analysisResult.type === 'translate') {
      return (
        <div className="translation-view">
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px',
            borderBottom: '1px solid #333',
            paddingBottom: '10px'
          }}>
            <h3 style={{ margin: 0, color: '#fbbf24' }}>🌐 Document Translation Preview</h3>
          </div>

          <div className="summary-content-box" style={{
            background: '#111',
            padding: '25px',
            borderRadius: '12px',
            border: '1px solid #333',
            marginBottom: '20px',
            maxHeight: '600px',
            overflowY: 'auto'
          }}>
            <FormattedResponse text={analysisResult.translation} />
          </div>

          <div style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
            <button
              className="download-btn"
              onClick={() => handleDownload(analysisResult.translation, `Translation_${docType.replace(/\s+/g, '_')}.txt`)}
              style={{
                background: '#fbbf24',
                color: '#000',
                border: 'none',
                padding: '12px 24px',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: 'bold',
                display: 'flex',
                alignItems: 'center',
                gap: '10px'
              }}
            >
              <span>📥</span> Download Translation (.txt)
            </button>
          </div>
        </div>
      );
    }
    if (analysisResult.type === 'verify') {
      return (
        <div className="verification-view">
          <div style={{
            background: '#222',
            padding: '20px',
            borderRadius: '12px',
            border: '1px solid #333',
            marginBottom: '20px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '0.9rem', color: '#888', marginBottom: '5px' }}>Verification Accuracy</div>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#fbbf24', marginBottom: '15px' }}>
              {analysisResult.confidence || '85%'}
            </div>
            <div className={`verdict-badge ${analysisResult.verdict.includes('ready') ? 'success' : 'warning'}`} style={{
              display: 'inline-block',
              padding: '10px 20px',
              borderRadius: '8px',
              fontWeight: 'bold',
              fontSize: '1rem',
              background: analysisResult.verdict.includes('ready') ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)',
              color: analysisResult.verdict.includes('ready') ? '#10b981' : '#f59e0b',
              border: `1px solid ${analysisResult.verdict.includes('ready') ? '#10b981' : '#f59e0b'}`
            }}>
              {analysisResult.verdict}
            </div>
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
      case 'login':
        return <Login onLoginSuccess={handleLoginSuccess} onSwitchToSignup={() => setCurrentView('signup')} />;

      case 'signup':
        return <Signup onSignupSuccess={() => setCurrentView('login')} onSwitchToLogin={() => setCurrentView('login')} />;

      case 'profile':
        return user ? (
          <UserProfile
            user={user}
            token={token!}
            onLogout={handleLogout}
            onBack={() => setCurrentView('home')}
          />
        ) : (
          <Login onLoginSuccess={handleLoginSuccess} onSwitchToSignup={() => setCurrentView('signup')} />
        );

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

                      const headers: any = {};
                      if (token) {
                        headers['Authorization'] = `Bearer ${token}`;
                      }

                      const resp = await fetch(`${config.API_BASE_URL}/legal/upload_doc`, {
                        method: 'POST',
                        headers,
                        body: form
                      });

                      if (resp.status === 401) {
                        handleLogout();
                        setUploadStatus('🔒 Session expired. Please login again.');
                        setIsLoading(false);
                        return;
                      }

                      const data = await resp.json();

                      if (resp.ok) {
                        setExtractedText(data.text);
                        setDocType(data.doc_type);

                        // Step 2: Analyze immediately
                        const analyzeResp = await fetch(`${config.API_BASE_URL}/legal/analyze_doc`, {
                          method: 'POST',
                          headers: {
                            'Content-Type': 'application/json',
                            'Authorization': token ? `Bearer ${token}` : ''
                          },
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
                      } else if (resp.status === 403) {
                        setUploadStatus(`⚠️ ${data.error || 'Upload limit reached. Please upgrade your subscription.'}`);
                      } else {
                        setUploadStatus(`Upload failed: ${data.detail || data.error || 'server error'}`);
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

            {requestSent ? (
              <div className="success-message" style={{
                padding: '40px',
                textAlign: 'center',
                background: '#1a1a1a',
                borderRadius: '12px',
                border: '1px solid #fbbf24',
                maxWidth: '600px',
                margin: '30px auto'
              }}>
                <div style={{ fontSize: '4rem', marginBottom: '20px' }}>✅</div>
                <h3 style={{ color: '#fbbf24', fontSize: '1.5rem', marginBottom: '10px' }}>Request Sent Successfully!</h3>
                <p style={{ color: '#ccc', fontSize: '1.1rem', marginBottom: '30px' }}>
                  We have received your consultation request. A lawyer will contact you within 24 hours at your provided email address.
                </p>
                <button
                  onClick={() => {
                    setRequestSent(false);
                    setCurrentView('home');
                  }}
                  className="contact-btn"
                >
                  Return to Home
                </button>
              </div>
            ) : (
              <form className="contact-form" onSubmit={async (e) => {
                e.preventDefault();
                const formData = new FormData(e.currentTarget);
                const data = {
                  name: formData.get('name') as string,
                  email: formData.get('email') as string,
                  phone: formData.get('phone') as string,
                  lawyer_type: formData.get('lawyer_type') as string,
                  budget: formData.get('budget') as string,
                  case_description: formData.get('case_description') as string
                };

                try {
                  setIsLoading(true);
                  const response = await fetch(`${config.API_BASE_URL}/api/contact_lawyer`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                  });

                  await response.json();

                  if (response.ok) {
                    setRequestSent(true);
                  } else {
                    alert('Failed to send request. Please try again.');
                  }
                } catch (error) {
                  alert('Error sending request. Please check your connection.');
                } finally {
                  setIsLoading(false);
                }
              }}>
                <div className="form-group">
                  <label htmlFor="name">Your Name *</label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    placeholder="Enter your full name"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="email">Your Email *</label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    placeholder="your.email@example.com"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="phone">Phone Number *</label>
                  <input
                    type="tel"
                    id="phone"
                    name="phone"
                    placeholder="+91 XXXXX XXXXX"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="lawyer_type">Type of Lawyer *</label>
                  <select id="lawyer_type" name="lawyer_type" required>
                    <option value="">Select lawyer type...</option>
                    <option value="Criminal Lawyer">Criminal Lawyer</option>
                    <option value="Civil Lawyer">Civil Lawyer</option>
                    <option value="Family Lawyer">Family Lawyer</option>
                    <option value="Corporate Lawyer">Corporate Lawyer</option>
                    <option value="Property Lawyer">Property Lawyer</option>
                    <option value="Tax Lawyer">Tax Lawyer</option>
                    <option value="Labor Lawyer">Labor & Employment Lawyer</option>
                    <option value="Immigration Lawyer">Immigration Lawyer</option>
                    <option value="Consumer Rights Lawyer">Consumer Rights Lawyer</option>
                    <option value="Constitutional Lawyer">Constitutional Lawyer</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="budget">
                    Budget: ₹{budgetValue.toLocaleString('en-IN')}
                  </label>
                  <input
                    type="range"
                    id="budget"
                    name="budget"
                    min="5000"
                    max="1000000"
                    step="5000"
                    value={budgetValue}
                    onChange={(e) => setBudgetValue(Number(e.target.value))}
                    className="budget-slider"
                    style={{
                      background: `linear-gradient(to right, #fbbf24 0%, #fbbf24 ${((budgetValue - 5000) / (1000000 - 5000)) * 100}%, #444 ${((budgetValue - 5000) / (1000000 - 5000)) * 100}%, #444 100%)`
                    }}
                    required
                  />
                  <div className="budget-labels">
                    <span>₹5,000</span>
                    <span>₹10,00,000</span>
                  </div>
                  <input
                    type="hidden"
                    name="budget"
                    value={`₹${budgetValue.toLocaleString('en-IN')}`}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="case_description">Describe Your Case *</label>
                  <textarea
                    id="case_description"
                    name="case_description"
                    placeholder="Please provide details about your legal issue..."
                    rows={6}
                    required
                  />
                </div>

                <button
                  type="submit"
                  className="contact-btn"
                  disabled={isLoading}
                >
                  {isLoading ? 'Sending...' : 'Send Request'}
                </button>
              </form>
            )}
            {!requestSent && (
              <button onClick={() => setCurrentView('home')} className="back-btn">
                ← Back to Home
              </button>
            )}
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

        <div className="nav-right" style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <button
            className="nav-btn subscription-btn"
            onClick={() => setCurrentView(user ? 'profile' : 'login')}
            style={{
              background: '#1a1a1a',
              color: '#fbbf24',
              border: '1px solid #fbbf24',
              padding: '8px 16px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: 'bold',
              fontSize: '0.9rem'
            }}
          >
            Subscription
          </button>

          <div style={{ position: 'relative' }}>
            <button
              className="nav-btn lang-btn"
              onClick={() => setShowLangs(!showLangs)}
              style={{
                background: '#1a1a1a',
                color: '#fbbf24',
                border: '1px solid #fbbf24',
                padding: '8px 16px',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: 'bold',
                fontSize: '0.9rem',
                display: 'flex',
                alignItems: 'center',
                gap: '5px'
              }}
            >
              {selectedLanguage} ▼
            </button>
            {showLangs && (
              <div className="lang-dropdown" style={{
                position: 'absolute',
                top: '100%',
                right: 0,
                marginTop: '5px',
                background: '#1a1a1a',
                border: '1px solid #333',
                borderRadius: '8px',
                overflow: 'hidden',
                zIndex: 1000,
                minWidth: '120px'
              }}>
                {languages.map(lang => (
                  <div
                    key={lang}
                    className="lang-option"
                    onClick={() => {
                      setSelectedLanguage(lang);
                      localStorage.setItem('specter_lang', lang);
                      setShowLangs(false);
                    }}
                    style={{
                      padding: '10px 15px',
                      color: '#fff',
                      cursor: 'pointer',
                      borderBottom: '1px solid #333',
                      transition: 'background 0.2s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = '#333'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    {lang}
                  </div>
                ))}
              </div>
            )}
          </div>

          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div
                onClick={() => setCurrentView('profile')}
                style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  background: '#fbbf24',
                  color: '#000',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 'bold',
                  cursor: 'pointer',
                  border: '2px solid #fff'
                }}
                title="View Profile"
              >
                {user.full_name?.charAt(0).toUpperCase()}
              </div>
            </div>
          ) : (
            <button
              className="nav-btn"
              onClick={() => setCurrentView('login')}
              style={{
                background: '#fbbf24',
                color: '#000',
                border: 'none',
                padding: '8px 20px',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: 'bold',
                fontSize: '0.9rem'
              }}
            >
              Login
            </button>
          )}
        </div>
      </nav>

      {/* Slide-out Sidebar */}
      <nav className={`side-nav ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-main">
          <ul className="sidebar-nav-links">
            <li className={currentView === 'home' ? 'active' : ''} onClick={() => {
              if (!user) { setCurrentView('login'); } else { setCurrentView('home'); }
              setSidebarOpen(false);
            }}>
              {t('home')}
            </li>
            <li onClick={() => {
              if (!user) { setCurrentView('login'); } else { setCurrentView('chat'); }
              setSidebarOpen(false);
            }}>SPECTER</li>
            <li onClick={() => {
              if (!user) { setCurrentView('login'); } else { setCurrentView('upload'); }
              setSidebarOpen(false);
            }}>{t('upload')}</li>
            <li onClick={() => {
              if (!user) { setCurrentView('login'); } else { setServicesOpen(true); }
              setSidebarOpen(false);
            }}>Legal Services</li>
            <li onClick={() => {
              if (!user) { setCurrentView('login'); } else { setCurrentView('contact'); }
              setSidebarOpen(false);
            }}>{t('contact')}</li>

            {user && (
              <li
                onClick={() => { handleLogout(); setSidebarOpen(false); }}
                style={{ color: '#ef4444', marginTop: '20px', borderTop: '1px solid #333', paddingTop: '20px' }}
              >
                Logout
              </li>
            )}
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

      {/* Upgrade Modal - Blocks app when limits exceeded */}
      {showUpgradeModal && usageStats && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.95)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10000
        }}>
          <div style={{
            background: '#1a1a1a',
            padding: '40px',
            borderRadius: '16px',
            border: '2px solid #fbbf24',
            maxWidth: '500px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '4rem', marginBottom: '20px' }}>⚠️</div>
            <h2 style={{ color: '#fbbf24', marginBottom: '20px' }}>Usage Limit Reached</h2>
            <p style={{ color: '#ccc', marginBottom: '30px', lineHeight: '1.6' }}>
              You've reached your monthly limit for the Free plan:
            </p>
            <div style={{ background: '#222', padding: '20px', borderRadius: '8px', marginBottom: '30px', textAlign: 'left' }}>
              <div style={{ marginBottom: '15px' }}>
                <span style={{ color: '#888' }}>Questions: </span>
                <span style={{ color: usageStats.questions.remaining <= 0 ? '#ef4444' : '#10b981', fontWeight: 'bold' }}>
                  {usageStats.questions.used}/{usageStats.questions.limit}
                </span>
              </div>
              <div>
                <span style={{ color: '#888' }}>Uploads: </span>
                <span style={{ color: usageStats.uploads.remaining <= 0 ? '#ef4444' : '#10b981', fontWeight: 'bold' }}>
                  {usageStats.uploads.used}/{usageStats.uploads.limit}
                </span>
              </div>
            </div>
            <p style={{ color: '#fff', marginBottom: '30px', fontSize: '1.1rem' }}>
              Upgrade to continue using SPECTER AI
            </p>
            <div style={{ display: 'flex', gap: '15px', justifyContent: 'center' }}>
              <button
                onClick={() => {
                  setShowUpgradeModal(false);
                  setCurrentView('profile');
                }}
                style={{
                  background: '#fbbf24',
                  color: '#000',
                  border: 'none',
                  padding: '15px 30px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: 'bold',
                  fontSize: '1rem'
                }}
              >
                View Plans & Upgrade
              </button>
              <button
                onClick={() => setShowUpgradeModal(false)}
                style={{
                  background: 'transparent',
                  color: '#888',
                  border: '1px solid #444',
                  padding: '15px 30px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '1rem'
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Voice Assistant */}
      <VoiceAssistant />
    </div>
  );
}

export default App;

export function FormattedResponse({ text }: { text: string }) {
  if (!text) return null;

  // Clean text for display
  const lines = text.split('\n');
  const elements: React.ReactNode[] = [];
  let listOpen = false;
  let listItems: React.ReactNode[] = [];

  const flushList = () => {
    if (listOpen && listItems.length) {
      elements.push(<ul key={`list-${elements.length}`} className="resp-list" style={{ marginTop: 8, marginBottom: 12, paddingLeft: 20 }}>{listItems}</ul>);
    }
    listOpen = false;
    listItems = [];
  };

  lines.forEach((raw, idx) => {
    let line = raw.trim();
    if (!line) {
      flushList();
      elements.push(<div key={`sp-${idx}`} style={{ height: 10 }} />);
      return;
    }

    // Handle Headers (e.g., **1. EXECUTIVE SUMMARY**)
    if (line.startsWith('**') && line.endsWith('**')) {
      flushList();
      const headerText = line.replace(/\*\*/g, '');
      elements.push(
        <h3 key={`hd-${idx}`} style={{
          color: '#fbbf24',
          marginTop: '20px',
          marginBottom: '10px',
          fontSize: '1.1rem',
          borderLeft: '4px solid #fbbf24',
          paddingLeft: '10px'
        }}>
          {headerText}
        </h3>
      );
      return;
    }

    // Handle Bullet Points
    if (line.startsWith('- ')) {
      listOpen = true;
      const content = line.slice(2).replace(/\*\*/g, '');
      listItems.push(<li key={`li-${idx}`} style={{ marginBottom: 6 }}>{content}</li>);
      return;
    }

    flushList();

    // Handle Bold Text within lines
    const parts = line.split(/(\*\*.*?\*\*)/g);
    const formattedLine = parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} style={{ color: '#fbbf24' }}>{part.replace(/\*\*/g, '')}</strong>;
      }
      return part;
    });

    elements.push(
      <div key={`tx-${idx}`} className="resp-line" style={{
        marginBottom: 8,
        whiteSpace: 'pre-line',
        color: '#eee'
      }}>
        {formattedLine}
      </div>
    );
  });

  flushList();
  return <div className="formatted-response" style={{ lineHeight: 1.7 }}>{elements}</div>;
}

export function LegalServicesPanel({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  if (!isOpen) return null;
  return (
    <div className="backdrop" onClick={onClose}>
      <div
        className="legal-services-modal bot-interface"
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


    </div >
  );
}
