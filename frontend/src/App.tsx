import React, { useState, useRef } from 'react';
import './App.css';

function App() {
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [library, setLibrary] = useState<any[]>([]);
  const [showLibrary, setShowLibrary] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const startCamera = async () => {
    try {
      console.log("Checking mediaDevices:", navigator.mediaDevices);
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
              // Automatically use HTTPS if the frontend is served via HTTPS
              const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
              const apiHost = `${protocol}//${window.location.hostname}:8000`;
              
              const response = await fetch(`${apiHost}/cards/scan`, {
                method: 'POST',
                body: formData,
              });
              const data = await response.json();
              setResult(data);
              setScanning(false);
              // Stop stream
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
      const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
      const apiHost = `${protocol}//${window.location.hostname}:8000`;
      
      const response = await fetch(`${apiHost}/cards/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...result.card_data,
          confidence: result.confidence,
          image_path: "" // Placeholder
        }),
      });
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
      const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
      const apiHost = `${protocol}//${window.location.hostname}:8000`;
      const response = await fetch(`${apiHost}/cards/`);
      const data = await response.json();
      setLibrary(data);
      setShowLibrary(true);
    } catch (err) {
      console.error("Fetch library failed:", err);
    }
  };

  const trainML = async () => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
      const apiHost = `${protocol}//${window.location.hostname}:8000`;
      const response = await fetch(`${apiHost}/cards/train-ml`, { method: 'POST' });
      const data = await response.json();
      alert(data.message);
    } catch (err) {
      console.error("ML training failed:", err);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>CardScope</h1>
        
        {!scanning && !result && !showLibrary && (
          <div className="menu-buttons">
            <button onClick={startCamera}>Start Scan</button>
            <button onClick={fetchLibrary}>My Library</button>
            <button onClick={trainML}>Train ML Model</button>
          </div>
        )}

        {showLibrary && (
          <div className="library-container">
            <h2>My Card Library</h2>
            <button onClick={() => setShowLibrary(false)}>Back to Menu</button>
            <div className="card-list">
              {library.length === 0 ? <p>No cards stored yet.</p> : library.map((card: any) => (
                <div key={card.id} className="card-item">
                  <div className="card-item-header">
                    <p><strong>{card.name}</strong> ({card.game})</p>
                    {card.price && <p className="card-price">${card.price}</p>}
                  </div>
                  <p>{card.set_code}-{card.card_number} | {card.rarity}</p>
                  {card.image_url && <img src={card.image_url} alt={card.name} className="card-thumbnail" />}
                </div>
              ))}
            </div>
          </div>
        )}

        {scanning && (
          <div className="camera-container">
            <video ref={videoRef} autoPlay playsInline muted />
            <button onClick={captureImage} className="capture-btn">Scan Card</button>
          </div>
        )}

        {result && (
          <div className="result-container">
            <h2>Result ({result.scan_method})</h2>
            <p>Confidence: {(result.confidence * 100).toFixed(1)}%</p>
            {result.card_data ? (
              <div className="card-info">
                {result.card_data.image_url && <img src={result.card_data.image_url} alt={result.card_data.name} className="card-preview-img" />}
                <p><strong>Name:</strong> {result.card_data.name}</p>
                <p><strong>Set:</strong> {result.card_data.set_code}-{result.card_data.card_number}</p>
                {result.card_data.price && <p><strong>Price:</strong> ${result.card_data.price}</p>}
                {result.card_data.rarity && <p><strong>Rarity:</strong> {result.card_data.rarity}</p>}
                {result.card_data.description && <p className="card-desc">{result.card_data.description}</p>}
                <button onClick={saveCard} className="save-btn">Save to Library</button>
              </div>
            ) : (
              <p>No card detected accurately.</p>
            )}
            <button onClick={() => setResult(null)}>Scan Another</button>
          </div>
        )}

        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </header>
    </div>
  );
}

export default App;
