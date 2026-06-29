# CareerPilot AI — Deployment Guide

This guide outlines deployment options for hosting **CareerPilot AI** (the Gradio interface and the MCP server) on Hugging Face Spaces, Render, and Railway.

---

## 🤖 Hugging Face Spaces (Gradio Dashboard)

Hugging Face Spaces is the easiest platform for hosting Gradio web apps for free.

### Setup Instructions
1. **Create an Account**: Sign up at [huggingface.co](https://huggingface.co).
2. **Create a New Space**:
   - Navigate to **Spaces** -> **Create new Space**.
   - Set a name (e.g., `careerpilot-ai`).
   - Select **Gradio** as the SDK.
   - Choose the **Blank** template.
   - Select **Public** or **Private** visibility.
   - Choose the **Free CPU Basic** hardware tier.
3. **Commit the Files**:
   Clone the repository Hugging Face creates for your Space, copy the CareerPilot project files into it, and push:
   ```bash
   git clone https://huggingface.co/spaces/your-username/careerpilot-ai
   cd careerpilot-ai
   # Copy all project files here (maintaining the folders: agents/, utils/, tests/, docs/)
   # Ensure requirements.txt and app.py are in the root directory
   git add .
   git commit -m "Initial commit of CareerPilot AI"
   git push origin main
   ```
4. **Build and Run**: Hugging Face automatically detects `requirements.txt` and `app.py`, runs the setup, and hosts the app on your space page!

---

## 🚀 Render (Web App & Background Worker)

Render can run the Gradio UI app containerized or as a Web Service.

### Setup Instructions
1. **Sign Up**: Register at [render.com](https://render.com).
2. **Deploy the Gradio UI Web Service**:
   - Click **New +** -> **Web Service**.
   - Connect your GitHub repository containing the CareerPilot code.
   - Set the following configurations:
     - **Name**: `careerpilot-ui`
     - **Environment**: `Docker` (Render automatically uses the project's root `Dockerfile`)
     - **Instance Type**: `Free` (or Starter)
   - Add Environment Variables under **Advanced**:
     - `PORT`: `7860`
     - `HOST`: `0.0.0.0`
     - `LOG_LEVEL`: `INFO`
   - Click **Deploy Web Service**. Render will build the Docker container and expose a public URL (e.g., `https://careerpilot-ui.onrender.com`).

---

## 🚂 Railway (Docker Compose Deploy)

Railway makes it easy to deploy applications with zero configuration. It automatically reads the `docker-compose.yml` or `Dockerfile`.

### Setup Instructions
1. **Register**: Register at [railway.app](https://railway.app).
2. **Create Project**:
   - Click **New Project** -> **Deploy from GitHub repo**.
   - Select your project repository.
   - Click **Deploy Now**.
3. **Configure Service**:
   - Navigate to the newly created service in your dashboard.
   - Go to **Variables** and ensure the following are defined:
     - `PORT`: `7860`
     - `HOST`: `0.0.0.0`
   - Go to **Settings** -> **Public Networking** -> Click **Generate Domain** to create a public URL.
4. **Deploy**: Railway builds the application using the Dockerfile and deploys the Gradio web portal.

---

## 🔒 Security Practices for Staging/Production

- **Environment variables**: Even though CareerPilot runs completely offline and requires no external API keys, if you extend the system to connect to a local database server, keep credentials protected in production configurations.
- **Persistent Volume Mounts**: Since the database is a local JSON file (`profile_store.json`), ensure your deployment platform has persistent storage mounted at `/app/profile_store.json` (like Render Disk Mounts or Railway Volumes) so that user states survive server redeployments or restarts.
