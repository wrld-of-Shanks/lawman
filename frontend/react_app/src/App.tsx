import React, { useState, useEffect } from 'react';
import './App.css';
import Auth from './Auth';
import Dashboard from './Dashboard';
import config from './config';

function App() {
  const [currentView, setCurrentView] = useState('home');
  const [chatMessage, setChatMessage] = useState('');
  const [chatResponse, setChatResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [servicesOpen, setServicesOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string>("");
  const [solutionsProblem, setSolutionsProblem] = useState('');
  const [solutionsResponse, setSolutionsResponse] = useState('');
  const [solutionsLoading, setSolutionsLoading] = useState(false);
  
  // Jurisdiction and Subscription State
  const [selectedJurisdiction, setSelectedJurisdiction] = useState<string>(() => localStorage.getItem('specter_jurisdiction') || '');
  const [subscriptionTier, setSubscriptionTier] = useState<string>('free'); // free, lite, specter
  const [usageStats, setUsageStats] = useState({ questions: 0, solutions: 0, uploads: 0 });
  const [showJurisdictionDialog, setShowJurisdictionDialog] = useState(false);
  const [showUpgradeDialog, setShowUpgradeDialog] = useState(false);
  const jurisdictions = ['India', 'United States', 'United Kingdom', 'Canada', 'Australia', 'Singapore', 'Other'];
  const selectedLanguage = 'English'; // Default to English for now
  
  const subscriptionLimits = {
    free: { questions: 10, solutions: 3, uploads: 0 },
    lite: { questions: 50, solutions: 25, uploads: 3 },
    specter: { questions: -1, solutions: -1, uploads: -1 } // -1 means unlimited
  };

  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<any>(null);

  const handleLogin = (userData: any) => {
    setUser(userData);
    setIsAuthenticated(true);
    // Load user subscription and usage data
    loadUserSubscriptionData(userData.id);
  };
  
  const loadUserSubscriptionData = async (userId: string) => {
    try {
      // Fetch subscription data from backend
      const response = await fetch(`${config.API_BASE_URL}/api/subscription-status/${userId}`);
      
      if (response.ok) {
        const data = await response.json();
        setSubscriptionTier(data.plan);
        
        // Load usage stats from local storage (for now)
        const savedUsage = JSON.parse(localStorage.getItem(`specter_usage_${userId}`) || '{"questions": 0, "solutions": 0, "uploads": 0}');
        setUsageStats(savedUsage);
      } else {
        // Fallback to local storage
        const savedTier = localStorage.getItem(`specter_subscription_${userId}`) || 'free';
        const savedUsage = JSON.parse(localStorage.getItem(`specter_usage_${userId}`) || '{"questions": 0, "solutions": 0, "uploads": 0}');
        setSubscriptionTier(savedTier);
        setUsageStats(savedUsage);
      }
    } catch (error) {
      console.error('Error loading subscription data:', error);
      // Fallback to local storage
      const savedTier = localStorage.getItem(`specter_subscription_${userId}`) || 'free';
      const savedUsage = JSON.parse(localStorage.getItem(`specter_usage_${userId}`) || '{"questions": 0, "solutions": 0, "uploads": 0}');
      setSubscriptionTier(savedTier);
      setUsageStats(savedUsage);
    }
  };
  
  const checkUsageLimit = (type: 'questions' | 'solutions' | 'uploads'): boolean => {
    const limits = subscriptionLimits[subscriptionTier as keyof typeof subscriptionLimits];
    const currentUsage = usageStats[type];
    
    if (limits[type] === -1) return true; // Unlimited
    return currentUsage < limits[type];
  };
  
  const incrementUsage = (type: 'questions' | 'solutions' | 'uploads') => {
    const newStats = { ...usageStats, [type]: usageStats[type] + 1 };
    setUsageStats(newStats);
    if (user?.id) {
      localStorage.setItem(`specter_usage_${user.id}`, JSON.stringify(newStats));
    }
  };
  
  const detectQuestionType = (message: string): 'general' | 'personal' => {
    const personalIndicators = [
      'my case', 'i have', 'i am facing', 'my problem', 'my situation',
      'help me with', 'what should i do', 'my husband', 'my wife', 'my employer',
      'i was', 'i got', 'i received', 'happened to me', 'my landlord',
      'my tenant', 'i want to file', 'i need to sue', 'my rights in this case'
    ];
    
    const lowerMessage = message.toLowerCase();
    return personalIndicators.some(indicator => lowerMessage.includes(indicator)) ? 'personal' : 'general';
  };

  // Check for existing authentication on app load
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // Verify token and get user data
      fetch(`${config.API_BASE_URL}/auth/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      .then(response => {
        if (response.ok) {
          return response.json();
        }
        throw new Error('Token invalid');
      })
      .then(userData => {
        setUser(userData);
        setIsAuthenticated(true);
      })
      .catch(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      });
    }
  }, []);

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

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        await fetch(`${config.API_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    }

    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return <Auth onLogin={handleLogin} />;
  }

  // If authenticated and on dashboard view, show dashboard
  if (currentView === 'dashboard' && isAuthenticated) {
    return <Dashboard user={user} onLogout={handleLogout} onNavigateHome={() => setCurrentView('home')} />;
  }

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
    
    // Check jurisdiction
    if (!selectedJurisdiction) {
      setShowJurisdictionDialog(true);
      return;
    }
    
    const questionType = detectQuestionType(chatMessage);
    const usageType = questionType === 'personal' ? 'solutions' : 'questions';
    
    // Check usage limits
    if (!checkUsageLimit(usageType)) {
      setShowUpgradeDialog(true);
      return;
    }
    
    setIsLoading(true);
    try {
      let prefixed = selectedLanguage === 'English' ? chatMessage : `Respond in ${selectedLanguage}. ${chatMessage}`;
      prefixed += ` [Jurisdiction: ${selectedJurisdiction}]`;
      
      const response = await fetch(`${config.API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: prefixed })
      });
      const data = await response.json();
      
      // Add solution indicator for personal legal issues
      let responseText = data.answer;
      if (questionType === 'personal') {
        responseText = `🔍 **Legal Solution Provided**\n\n${responseText}\n\n---\n*This is a personalized legal solution based on ${selectedJurisdiction} law. Consult a lawyer for specific advice.*`;
      }
      
      setChatResponse(responseText);
      incrementUsage(usageType);
    } catch (error) {
      setChatResponse('Error connecting to SPECTER. Please try again.');
    }
    setIsLoading(false);
  };

  const handleTranslate = async () => {
    if (!chatResponse.trim() || selectedLanguage === 'English') return;
    try {
      const resp = await fetch(`${config.TRANSLATE_API_URL}/translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: chatResponse, target_lang: selectedLanguage })
      });
      const data = await resp.json();
      if (data.translated) setChatResponse(data.translated);
    } catch(e) {}
  };

  const handleSolutionsSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!solutionsProblem.trim()) return;
    
    setSolutionsLoading(true);
    setSolutionsResponse('');
    
    try {
      const solutionsMessage = `provide legal solutions for this problem: ${solutionsProblem}`;
      const response = await fetch(`${config.API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: solutionsMessage })
      });
      const data = await response.json();
      setSolutionsResponse(data.answer);
    } catch (error) {
      setSolutionsResponse('Error connecting to SPECTER. Please try again.');
    }
    setSolutionsLoading(false);
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
                  setUploadStatus('Please select a file first');
                  return;
                }

                // Check jurisdiction
                if (!selectedJurisdiction) {
                  setShowJurisdictionDialog(true);
                  return;
                }

                // Check usage limits
                if (!checkUsageLimit('uploads')) {
                  setShowUpgradeDialog(true);
                  return;
                }

                setUploadStatus('Uploading...');
                const formData = new FormData();
                formData.append('file', selectedFile);
                formData.append('jurisdiction', selectedJurisdiction);

                try {
                  const response = await fetch(`${config.API_BASE_URL}/upload`, {
                    method: 'POST',
                    body: formData
                  });
                  const data = await response.json();
                  setUploadStatus(`Upload successful: ${data.message}`);
                  incrementUsage('uploads');
                } catch (error) {
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
            <form className="solutions-form" onSubmit={handleSolutionsSubmit}>
              <textarea 
                value={solutionsProblem}
                onChange={(e) => setSolutionsProblem(e.target.value)}
                placeholder="Describe your legal problem in detail..."
                className="solutions-input"
                rows={4}
              />
              <button 
                className="solutions-btn" 
                type="submit" 
                disabled={solutionsLoading || !solutionsProblem.trim()}
              >
                {solutionsLoading ? 'Analyzing...' : 'Get Legal Solutions'}
              </button>
            </form>
            
            {solutionsResponse && (
              <div className="solutions-response">
                <h3>Legal Solutions:</h3>
                <FormattedResponse text={solutionsResponse} />
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
              <button onClick={() => setCurrentView('chat')} className="feature-btn">
                <span className="feature-icon">💬</span>
                <span className="feature-text">{t('ask')}</span>
              </button>
              
              <button onClick={() => setCurrentView('upload')} className="feature-btn">
                <span className="feature-icon">📄</span>
                <span className="feature-text">{t('upload_docs')}</span>
              </button>
              
              
              <button onClick={() => setCurrentView('chat')} className="feature-btn specter-btn" style={{
                background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
                color: '#000',
                fontWeight: 'bold',
                boxShadow: '0 4px 15px rgba(255, 215, 0, 0.3)',
                transform: 'scale(1.05)',
                border: '2px solid #FFD700'
              }}>
                <span className="feature-icon">🤖</span>
                <span className="feature-text">SPECTER</span>
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
          <div className="header-right">
          {selectedJurisdiction && (
            <div className="jurisdiction-indicator" style={{ 
              marginRight: '10px', 
              padding: '4px 8px', 
              background: 'rgba(255,215,0,0.2)', 
              borderRadius: '4px',
              fontSize: '12px',
              color: '#FFD700'
            }}>
              📍 {selectedJurisdiction}
            </div>
          )}
          </div>
          {isAuthenticated && (
            <button className="status-button" onClick={() => setCurrentView('dashboard')}>
              Status
            </button>
          )}
        </div>
      </nav>

      {/* Slide-out Sidebar */}
      <nav className={`side-nav ${sidebarOpen ? 'open' : ''}`}>
        <ul>
          {isAuthenticated && (
            <li className="user-info">
              {user?.full_name || 'User'}
            </li>
          )}
          <li className={currentView === 'home' ? 'active' : ''} onClick={() => { setCurrentView('home'); setSidebarOpen(false); }}>
            {t('home')}
          </li>
          <li onClick={() => { setCurrentView('chat'); setSidebarOpen(false); }}>{t('chat')}</li>
          <li onClick={() => { setCurrentView('upload'); setSidebarOpen(false); }}>{t('upload')}</li>
          <li onClick={() => { setCurrentView('solutions'); setSidebarOpen(false); }}>{t('solutions')}</li>
          <li onClick={() => { setCurrentView('contact'); setSidebarOpen(false); }}>{t('contact')}</li>
          {isAuthenticated && (
            <>
              <li onClick={() => { setCurrentView('dashboard'); setSidebarOpen(false); }}>Dashboard</li>
              <li onClick={() => { handleLogout(); setSidebarOpen(false); }}>Logout</li>
            </>
          )}
        </ul>
      </nav>
      {sidebarOpen && <div className="backdrop" onClick={() => setSidebarOpen(false)} />}
      <LegalServicesPanel isOpen={servicesOpen} onClose={() => setServicesOpen(false)} />
      <JurisdictionDialog 
        isOpen={showJurisdictionDialog} 
        onClose={() => setShowJurisdictionDialog(false)}
        onSelect={(jurisdiction: string) => {
          setSelectedJurisdiction(jurisdiction);
          localStorage.setItem('specter_jurisdiction', jurisdiction);
          setShowJurisdictionDialog(false);
        }}
        jurisdictions={jurisdictions}
      />
      <UpgradeDialog 
        isOpen={showUpgradeDialog}
        onClose={() => setShowUpgradeDialog(false)}
        currentTier={subscriptionTier}
        usageStats={usageStats}
        limits={subscriptionLimits}
        user={user}
        setSubscriptionTier={setSubscriptionTier}
        setUsageStats={setUsageStats}
        loadUserSubscriptionData={loadUserSubscriptionData}
      />

      {/* Main Content */}
      <main className="main-area">
        {renderContent()}
      </main>

      {/* Bottom Left Scroll Indicator */}
      <div className="scroll-indicator">
        <span>scroll down</span>
        <div className="scroll-arrow">↓</div>
      </div>

      {/* Footer with Policy Links */}
      <footer style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        background: 'rgba(0, 0, 0, 0.9)',
        padding: '10px 20px',
        fontSize: '12px',
        color: '#888',
        textAlign: 'center',
        borderTop: '1px solid #333',
        zIndex: 1000
      }}>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', flexWrap: 'wrap' }}>
          <a href="/privacy-policy.html" target="_blank" style={{ color: '#FFD700', textDecoration: 'none' }}>Privacy Policy</a>
          <a href="/terms-conditions.html" target="_blank" style={{ color: '#FFD700', textDecoration: 'none' }}>Terms & Conditions</a>
          <a href="/refund-policy.html" target="_blank" style={{ color: '#FFD700', textDecoration: 'none' }}>Refund Policy</a>
          <a href="/contact.html" target="_blank" style={{ color: '#FFD700', textDecoration: 'none' }}>Contact Us</a>
          <a href="/shipping-policy.html" target="_blank" style={{ color: '#FFD700', textDecoration: 'none' }}>Shipping Policy</a>
        </div>
        <div style={{ marginTop: '5px', fontSize: '10px' }}>
          © 2024 SPECTER Legal Assistant. All rights reserved. | Powered by AI Technology
        </div>
      </footer>
    </div>
  );
}

// Jurisdiction Selection Dialog
function JurisdictionDialog({ isOpen, onClose, onSelect, jurisdictions }: any) {
  if (!isOpen) return null;
  return (
    <div className="backdrop" onClick={onClose}>
      <div className="bot-interface" style={{ maxWidth: 500, margin: '100px auto' }} onClick={(e) => e.stopPropagation()}>
        <h2>Select Your Jurisdiction</h2>
        <p>Which country's legal system should I apply?</p>
        <div style={{ display: 'grid', gap: '10px', marginTop: '20px' }}>
          {jurisdictions.map((jurisdiction: string) => (
            <button 
              key={jurisdiction}
              className="chat-btn" 
              onClick={() => onSelect(jurisdiction)}
              style={{ padding: '12px', textAlign: 'left' }}
            >
              {jurisdiction}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

// Upgrade Dialog with Razorpay Integration
function UpgradeDialog({ isOpen, onClose, currentTier, usageStats, limits, user, setSubscriptionTier, setUsageStats, loadUserSubscriptionData }: any) {
  const [isProcessing, setIsProcessing] = useState(false);
  
  if (!isOpen) return null;

  const handlePayment = async (plan: string) => {
    if (!user) {
      alert('Please login to upgrade your subscription');
      return;
    }

    setIsProcessing(true);
    
    try {
      // Create payment order
      const response = await fetch(`${config.API_BASE_URL}/api/create-payment-order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plan: plan,
          user_id: user.id,
          user_email: user.email,
          user_name: user.full_name || user.email
        })
      });
      
      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.message || 'Failed to create payment order');
      }
      
      const { order_id, amount, currency, key_id, description } = result.data;
      
      // Initialize Razorpay
      const options = {
        key: key_id,
        amount: amount,
        currency: currency,
        name: 'SPECTER Legal Assistant',
        description: description,
        order_id: order_id,
        handler: async function (response: any) {
          try {
            // Verify payment
            const verifyResponse = await fetch(`${config.API_BASE_URL}/api/verify-payment`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
                user_id: user.id
              })
            });
            
            const verifyResult = await verifyResponse.json();
            
            if (verifyResult.success) {
              alert('Payment successful! Your subscription has been upgraded.');
              setSubscriptionTier(plan);
              setUsageStats({ questions: 0, solutions: 0, uploads: 0 }); // Reset usage
              onClose();
              // Reload subscription data
              loadUserSubscriptionData(user.id);
            } else {
              alert('Payment verification failed. Please contact support.');
            }
          } catch (error) {
            console.error('Payment verification error:', error);
            alert('Payment verification failed. Please contact support.');
          }
        },
        prefill: {
          name: user.full_name || user.email,
          email: user.email,
          contact: user.phone || ''
        },
        theme: {
          color: '#FFD700'
        },
        modal: {
          ondismiss: function() {
            setIsProcessing(false);
          }
        }
      };
      
      // Load Razorpay script and open payment modal
      const script = document.createElement('script');
      script.src = 'https://checkout.razorpay.com/v1/checkout.js';
      script.onload = () => {
        const rzp = new (window as any).Razorpay(options);
        rzp.open();
      };
      document.body.appendChild(script);
      
    } catch (error) {
      console.error('Payment error:', error);
      alert('Failed to initiate payment. Please try again.');
      setIsProcessing(false);
    }
  };

  return (
    <div className="backdrop" onClick={onClose}>
      <div className="bot-interface" style={{ maxWidth: 600, margin: '80px auto' }} onClick={(e) => e.stopPropagation()}>
        <h2>Upgrade Required</h2>
        <p>You have reached your limit for this feature under your current plan.</p>
        
        <div style={{ margin: '20px 0', padding: '15px', background: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}>
          <h3>Current Plan: {currentTier.toUpperCase()}</h3>
          <p>Questions: {usageStats.questions}/{limits[currentTier].questions === -1 ? '∞' : limits[currentTier].questions}</p>
          <p>Solutions: {usageStats.solutions}/{limits[currentTier].solutions === -1 ? '∞' : limits[currentTier].solutions}</p>
          <p>Uploads: {usageStats.uploads}/{limits[currentTier].uploads === -1 ? '∞' : limits[currentTier].uploads}</p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', margin: '20px 0' }}>
          <div style={{ padding: '15px', border: '2px solid #FFD700', borderRadius: '8px' }}>
            <h4>Lite Plan - ₹299</h4>
            <p>50 Questions, 25 Solutions, 3 Uploads</p>
            <button 
              className="chat-btn" 
              style={{ width: '100%', marginTop: '10px' }}
              onClick={() => handlePayment('lite')}
              disabled={isProcessing}
            >
              {isProcessing ? 'Processing...' : 'Upgrade to Lite'}
            </button>
          </div>
          <div style={{ padding: '15px', border: '2px solid #FFD700', borderRadius: '8px', background: 'rgba(255,215,0,0.1)' }}>
            <h4>SPECTER Plan - ₹499</h4>
            <p>Unlimited Everything + Priority</p>
            <button 
              className="chat-btn" 
              style={{ width: '100%', marginTop: '10px' }}
              onClick={() => handlePayment('specter')}
              disabled={isProcessing}
            >
              {isProcessing ? 'Processing...' : 'Upgrade to SPECTER'}
            </button>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
          <button className="back-btn" onClick={onClose} disabled={isProcessing}>Close</button>
        </div>
        
        <div style={{ marginTop: '15px', fontSize: '12px', color: '#888', textAlign: 'center' }}>
          <p>🔒 Secure payment powered by Razorpay</p>
          <p>Supports UPI, Cards, Net Banking & Wallets</p>
        </div>
      </div>
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
