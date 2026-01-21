# CardScope - Trading Card Scanner

CardScope is a local-first, offline-capable trading card scanning application. It now includes **SaaS features** such as user authentication and multi-tenancy, while retaining its core local-first architecture.

## 🚀 SaaS Features
- **User Authentication**: Sign up and Login to your personal collection.
- **Secure API**: JWT-based authentication for all card and scan operations.
- **Multi-tenancy**: Your library is private and isolated from other users.
- **Cloud Ready**: Easily deployable to AWS with persistent storage (S3) and managed database (RDS).

## 📱 Opening on your Phone

Since CardScope is a **Progressive Web App (PWA)**, you can open it on your phone and even install it as a native-like app:

1.  **Ensure both devices are on the same Wi-Fi network.**
2.  **Find your computer's local IP address** (e.g., `192.168.1.133`).
3.  **Run the app** on your computer:
    ```bash
    python run.py
    ```
4.  **Open your phone's browser** and go to: `https://<your-computer-ip>:3000` (Note the **HTTPS**)
5.  **Bypass the security warning**: Since we are using a self-signed certificate, your browser will show a "Your connection is not private" warning. 
    *   On **Chrome**: Click "Advanced" -> "Proceed to <IP> (unsafe)".
    *   On **Safari**: Click "Show Details" -> "visit this website" -> "Visit Website".
6.  **Mixed Content Warning**: Because the frontend uses HTTPS (for camera) and the backend uses HTTP, you might need to allow "Insecure content" or "Mixed content" in your browser settings for your computer's IP if the app fails to connect to the backend.
7.  **Install as App**:
    *   **iOS (Safari)**: Tap the "Share" icon and select "Add to Home Screen".
    *   **Android (Chrome)**: Tap the three dots and select "Install app" or "Add to Home screen".

> **Note**: The app uses the phone's camera via the `getUserMedia` API. Most modern browsers require a secure context (HTTPS) for camera access. However, `localhost` and local network IPs are often treated as "potentially secure" for development. 

### If the camera doesn't start (Chrome on Android):
1. Open Chrome on your phone.
2. Go to `chrome://flags/#unsafely-treat-insecure-origin-as-secure`.
3. Enable the flag.
4. Add your computer's IP and port to the list (e.g., `http://192.168.1.133:3000`).
5. Relaunch Chrome.

### If the camera doesn't start (Safari on iOS):
iOS Safari is more restrictive. To use the camera over the local network, you typically **must** use HTTPS.

#### Option 1: Run with HTTPS (Recommended)
You can try to run the frontend with HTTPS enabled:
```bash
cd frontend
$env:HTTPS='true'; npm start
```
*Note: You will see a certificate warning in your browser; click "Advanced" and "Proceed" to continue.*

#### Option 2: Use a Tunnel (ngrok)
If you have `ngrok` installed, you can expose your local server securely:
```bash
ngrok http 3000
```
Then open the `https://...` URL provided by ngrok on your phone.

## ☁️ Deployment to AWS

CardScope is cloud-ready and can be deployed to AWS using the following architecture:

### 🏗️ Recommended Architecture
- **Backend**: AWS App Runner or ECS (Fargate)
- **Frontend**: AWS S3 + CloudFront (Static Web Hosting)
- **Database**: AWS RDS (PostgreSQL)
- **Storage**: AWS S3 (for card scan images)

### 1. Backend (FastAPI) on AWS App Runner
1. **Containerize**: Use the provided `backend.Dockerfile`.
2. **ECR**: Push the image to Amazon Elastic Container Registry (ECR).
3. **App Runner**: Create a new service in App Runner, pointing to your ECR image.
4. **Environment Variables**: Configure the following in App Runner:
   - `DATABASE_URL`: Connection string to your RDS instance (e.g., `postgresql://user:password@host:5432/db`).
   - `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`: IAM credentials with S3 access.
   - `AWS_STORAGE_BUCKET_NAME`: The name of your S3 bucket for images.

### 2. Frontend (React) on S3 + CloudFront
1. **Build**: Run `npm run build` in the `frontend` directory.
2. **S3**: Create an S3 bucket and upload the contents of the `build` folder. Enable "Static Website Hosting".
3. **CloudFront**: Create a distribution pointing to your S3 bucket for global CDN and HTTPS.
4. **API URL**: Ensure the `apiHost` in `App.tsx` correctly points to your App Runner service URL.

### 3. Database (RDS)
- Launch a PostgreSQL instance on AWS RDS.
- Update the `DATABASE_URL` in your backend configuration to point to this instance.
- Ensure security groups allow traffic from the backend to the RDS port (5432).

### 4. Storage (S3)
- Create an S3 bucket for storing card scans.
- The backend will automatically upload images if `AWS_STORAGE_BUCKET_NAME` is provided.

---

## 🐳 Deployment with Docker

The easiest way to deploy CardScope in a production-like environment is using **Docker Compose**.

### 1. Prerequisites
- [Docker](https://docs.docker.com/get-docker/) installed on your machine.
- [Docker Compose](https://docs.docker.com/compose/install/) installed.

### 2. Running with Docker Compose
1.  **Clone the repository**.
2.  **Create a `.env` file** in the root directory (optional, for AWS features):
    ```env
    AWS_ACCESS_KEY_ID=your_key
    AWS_SECRET_ACCESS_KEY=your_secret
    AWS_STORAGE_BUCKET_NAME=your_bucket
    AWS_REGION=us-east-1
    ```
3.  **Start the containers**:
    ```bash
    docker-compose up --build
    ```
4.  **Access the app**:
    - Frontend: `http://localhost:3000`
    - Backend API: `http://localhost:8000`

### 3. Production Considerations
- **HTTPS**: For production, you should wrap the services in a reverse proxy like **Nginx** or **Traefik** with Let's Encrypt for SSL certificates.
- **Database**: While the Docker setup uses SQLite by default, for high availability, use a managed database like **AWS RDS** and update the `DATABASE_URL`.
- **Image Storage**: Use **AWS S3** for persistent storage of scanned card images, as local container storage is ephemeral.

---

## 🚀 Quick Start

The easiest way to run the application is using the provided `run.py` script.

### Prerequisites

- **Python 3.11+**
- **Node.js & npm**
- **Poetry** (Python package manager)
- **Tesseract OCR**: Must be installed on your system.
  - Windows: [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
  - Linux: `sudo apt install tesseract-ocr`
  - macOS: `brew install tesseract`

### Running the App

1. **Clone the repository** (if you haven't already).
2. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```
3. **Run the orchestration script**:
   ```bash
   python run.py
   ```

This script will:
- Install backend dependencies via Poetry.
- Start the FastAPI backend at `http://localhost:8000`.
- Start the React PWA frontend at `http://localhost:3000`.

---

## 🛠️ Architecture

### Backend (FastAPI + CV Pipeline)
- **FastAPI**: Handles API requests.
- **OpenCV**: Performs image processing (edge detection, perspective correction).
- **Tesseract OCR**: Extracts text from card images.
- **SQLite + SQLAlchemy**: Local-first database for card references and scan history.
- **Failsafe Path**: If visual recognition fails, the system attempts to extract card codes (e.g., `LOB-001`) and matches them against the local reference database.

### Frontend (React PWA)
- **React + TypeScript**: Modern UI components.
- **Web MediaDevices API**: Accesses the phone's camera directly from the browser.
- **Service Workers**: Enables offline functionality and PWA installation.
- **IndexedDB**: Local cache for metadata.

---

## 🗃️ Database Setup

The app automatically creates a SQLite database (`sql_app.db`) on the first run. 

To load sample reference data for testing the failsafe path:
```bash
poetry run python -m backend.app.load_sample_data
```

---

## 🧠 Failsafe Recognition Logic

The system uses a dual-path recognition strategy:
1. **Primary Path (Visual)**: Scans the entire card and attempts to match the name/artwork.
2. **Failsafe Path (Code)**: Focuses on the bottom region of the card to extract alphanumeric codes (e.g., `SET-NUM`). This provides 100% accurate matching even when the artwork is partially obscured or OCR confidence is low.

---

## 🔐 Privacy

CardScope is designed to be **local-first but SaaS-ready**. Your scans and data are tied to your account. In the default local setup, data remains on your machine in a SQLite database. When deployed to the cloud, data is stored securely in your managed database and S3 bucket.
