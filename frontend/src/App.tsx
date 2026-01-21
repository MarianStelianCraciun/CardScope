import React, { useState, useRef, useEffect } from 'react';
import './App.css';
import { Camera, Library, Brain, LogOut, X, Save, RefreshCw, ChevronLeft } from 'lucide-react';

function App() {
  const [user, setUser] = useState<any>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [library, setLibrary] = useState<any[]>([]);
  const [showLibrary, setShowLibrary] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Set initial user if token exists (simplified)
  useEffect(() => {
    if (token) {
      setUser({ email: 'User' }); // In real app, fetch user profile
    }
  }, [token]);

  const getApiHost = () => {
    // Force http for backend as it doesn't currently support HTTPS
    return `http://${window.location.hostname}:8000`;
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);

      const response = await fetch(`${getApiHost()}/token`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        setToken(data.access_token);
        setUser({ email });
      } else {
        alert("Login failed");
      }
    } catch (err) {
      console.error("Login error:", err);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`${getApiHost()}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        alert("Registration successful! Please login.");
        setAuthMode('login');
      } else {
        const data = await response.json();
        alert(`Registration failed: ${data.detail}`);
      }
    } catch (err) {
      console.error("Registration error:", err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const startCamera = async () => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert("Camera API (getUserMedia) is not supported in this browser or context (requires HTTPS).");
        return;
      }
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setScanning(true);
      }
    } catch (err: any) {
      console.error("Error accessing camera:", err);
      alert(`Could not access camera: ${err.message || err}`);
    }
  };

  const captureImage = () => {
    if (videoRef.current && canvasRef.current) {
      const context = canvasRef.current.getContext('2d');
      if (context) {
        canvasRef.current.width = videoRef.current.videoWidth;
        canvasRef.current.height = videoRef.current.videoHeight;
        context.drawImage(videoRef.current, 0, 0);
        
        canvasRef.current.toBlob(async (blob) => {
          if (blob) {
            const formData = new FormData();
            formData.append('file', blob, 'scan.jpg');
            
            try {
              const response = await fetch(`${getApiHost()}/cards/scan`, {
                method: 'POST',
                headers: {
                  'Authorization': `Bearer ${token}`
                },
                body: formData,
              });
              if (response.status === 401) return handleLogout();
              const data = await response.json();
              setResult(data);
              setScanning(false);
              const stream = videoRef.current?.srcObject as MediaStream;
              stream?.getTracks().forEach(track => track.stop());
            } catch (err) {
              console.error("Scan failed:", err);
            }
          }
        }, 'image/jpeg');
      }
    }
  };

  const saveCard = async () => {
    if (!result || !result.card_data) return;

    try {
      const response = await fetch(`${getApiHost()}/cards/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...result.card_data,
          confidence: result.confidence,
          image_path: result.card_data.image_path || ""
        }),
      });
      if (response.status === 401) return handleLogout();
      if (response.ok) {
        alert("Card saved to library!");
        setResult(null);
      }
    } catch (err) {
      console.error("Save failed:", err);
    }
  };

  const fetchLibrary = async () => {
    try {
      const response = await fetch(`${getApiHost()}/cards/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.status === 401) return handleLogout();
      const data = await response.json();
      setLibrary(data);
      setShowLibrary(true);
    } catch (err) {
      console.error("Fetch library failed:", err);
    }
  };

  const trainML = async () => {
    try {
      const response = await fetch(`${getApiHost()}/cards/train-ml`, { 
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.status === 401) return handleLogout();
      const data = await response.json();
      alert(data.message);
    } catch (err) {
      console.error("ML training failed:", err);
    }
  };

  if (!token) {
    return (
      <div className="App">
        <div className="auth-wrapper">
          <div className="auth-container">
            <h1 className="app-logo">CardScope</h1>
            <h2>{authMode === 'login' ? 'Sign in' : 'Create account'}</h2>
            <form className="auth-form" onSubmit={authMode === 'login' ? handleLogin : handleRegister}>
              <input 
                type="email" 
                placeholder="Email or phone" 
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
                required 
              />
              <input 
                type="password" 
                placeholder="Enter your password" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                required 
              />
              <button type="submit" className="primary-btn">
                {authMode === 'login' ? 'Next' : 'Register'}
              </button>
            </form>
            <p className="auth-toggle" onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}>
              {authMode === 'login' ? "Create account" : "Sign in instead"}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="app-header">
        <div className="app-logo">CardScope</div>
        <div className="user-nav">
          <span className="user-email">{user?.email}</span>
          <button onClick={handleLogout} className="logout-btn">
            <LogOut size={16} />
          </button>
        </div>
      </header>

      <main className="main-content">
        {!scanning && !result && !showLibrary && (
          <div className="menu-grid">
            <div className="action-card" onClick={startCamera}>
              <Camera size={48} />
              <span>Start Scan</span>
            </div>
            <div className="action-card" onClick={fetchLibrary}>
              <Library size={48} />
              <span>My Library</span>
            </div>
            <div className="action-card" onClick={trainML}>
              <Brain size={48} />
              <span>Train ML Model</span>
            </div>
          </div>
        )}

        {showLibrary && (
          <div className="library-section">
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
              <button className="secondary-btn" onClick={() => setShowLibrary(false)}>
                <ChevronLeft size={20} />
              </button>
              <h2 style={{ margin: 0 }}>My Collection</h2>
            </div>
            <div className="library-grid">
              {library.length === 0 ? (
                <p>No cards stored yet.</p>
              ) : (
                library.map((card: any) => (
                  <div key={card.id} className="card-grid-item">
                    <div className="card-thumb-wrapper">
                      {card.image_url ? (
                        <img src={card.image_url} alt={card.name} />
                      ) : (
                        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#ccc' }}>
                          <Camera size={32} />
                        </div>
                      )}
                    </div>
                    <div className="card-grid-info">
                      <h4>{card.name}</h4>
                      <p>{card.game}</p>
                      {card.price && <p className="card-price">${card.price}</p>}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {scanning && (
          <div className="scanner-viewport">
            <video ref={videoRef} autoPlay playsInline muted />
            <div className="viewfinder-overlay">
              <div className="viewfinder-rect" />
            </div>
            <button className="close-scanner" onClick={() => {
              setScanning(false);
              const stream = videoRef.current?.srcObject as MediaStream;
              stream?.getTracks().forEach(track => track.stop());
            }}>
              <X size={24} />
            </button>
            <div className="scanner-actions">
              <button onClick={captureImage} className="capture-fab">
                <div style={{ width: '60px', height: '60px', borderRadius: '50%', border: '4px solid #1a73e8' }} />
              </button>
            </div>
          </div>
        )}

        {result && (
          <div className="detail-sheet">
            <div className="detail-header">
              <div>
                <h2 style={{ margin: '0 0 4px 0' }}>Scan Result</h2>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <span className="chip">{result.scan_method} match</span>
                  <span className="chip">{(result.confidence * 100).toFixed(0)}% confidence</span>
                </div>
              </div>
              <button className="secondary-btn" style={{ padding: '8px' }} onClick={() => setResult(null)}>
                <X size={20} />
              </button>
            </div>

            {result.card_data ? (
              <div className="card-grid-display">
                <img 
                  src={result.card_data.image_url || 'https://via.placeholder.com/150x210'} 
                  alt={result.card_data.name} 
                  className="card-image-main" 
                />
                <div className="card-details-text">
                  <h3>{result.card_data.name}</h3>
                  <p style={{ color: '#5f6368', fontSize: '0.875rem' }}>{result.card_data.game}</p>
                  <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
                    {result.card_data.price && (
                      <span className="chip price-chip">${result.card_data.price}</span>
                    )}
                    {result.card_data.rarity && (
                      <span className="chip">{result.card_data.rarity}</span>
                    )}
                  </div>
                  <p className="card-description">{result.card_data.description}</p>
                  
                  <div style={{ marginTop: '24px', display: 'flex', gap: '12px' }}>
                    <button onClick={saveCard} className="primary-btn" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Save size={18} /> Save to Library
                    </button>
                    <button onClick={() => setResult(null)} className="secondary-btn" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <RefreshCw size={18} /> Rescan
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <p>No card detected. Please try again with better lighting.</p>
            )}
          </div>
        )}

        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </main>
    </div>
  );
}

export default App;
