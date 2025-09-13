# Doc2LaTeX Web Deployment Guide

## Quick Start (Local Development)

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements-web.txt
   ```

2. **Run the development server:**
   ```bash
   python app.py
   ```

3. **Access the application:**
   Open http://localhost:5000 in your browser

## Docker Deployment

### Option 1: Docker Compose (Recommended)

1. **Build and start services:**
   ```bash
   docker-compose up -d
   ```

2. **Access your application:**
   - HTTP: http://your-domain.com
   - Local: http://localhost

### Option 2: Docker Only

1. **Build the image:**
   ```bash
   docker build -t doc2latex-web .
   ```

2. **Run the container:**
   ```bash
   docker run -d -p 5000:5000 \
     -v $(pwd)/uploads:/app/uploads \
     -v $(pwd)/web_output:/app/web_output \
     doc2latex-web
   ```

## Cloud Deployment Options

### 1. AWS EC2 / Google Cloud / Azure VM

1. **Setup VM with Docker:**
   ```bash
   # Install Docker and Docker Compose
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   sudo curl -L "https://github.com/docker-compose/docker-compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Deploy application:**
   ```bash
   git clone your-repository
   cd Doc2LaTeX_Project
   docker-compose up -d
   ```

3. **Configure firewall:**
   - Open ports 80 and 443
   - Set up security groups

### 2. Heroku Deployment

1. **Install Heroku CLI and login:**
   ```bash
   heroku login
   ```

2. **Create Heroku app:**
   ```bash
   heroku create your-app-name
   ```

3. **Set buildpacks:**
   ```bash
   heroku buildpacks:set heroku/python
   heroku buildpacks:add --index 1 https://github.com/Scalingo/tex-buildpack
   ```

4. **Deploy:**
   ```bash
   git push heroku main
   ```

### 3. Digital Ocean App Platform

1. **Connect GitHub repository**
2. **Configure build settings:**
   - Build Command: `pip install -r requirements-web.txt`
   - Run Command: `gunicorn --bind 0.0.0.0:$PORT app:app`

### 4. Railway / Render / Vercel

Follow their respective documentation for Python Flask apps.

## Production Configuration

### Environment Variables

Set these environment variables in production:

```bash
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key
MAX_CONTENT_LENGTH=16777216  # 16MB
```

### SSL Certificate

1. **Let's Encrypt (Free):**
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

2. **Update nginx.conf** to use SSL configuration

### Performance Optimization

1. **Use Redis for session storage** (optional)
2. **Implement file cleanup** for old uploads
3. **Add rate limiting** to prevent abuse
4. **Monitor with tools** like New Relic or DataDog

## File Structure

```
Doc2LaTeX_Project/
├── app.py                 # Main Flask application
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   └── preview.html
├── src/                   # Conversion logic
├── config/                # Configuration files
├── uploads/               # User uploads (create automatically)
├── web_output/            # Generated files (create automatically)
├── requirements-web.txt   # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Multi-container setup
└── nginx.conf            # Nginx configuration
```

## Security Considerations

1. **File Upload Security:**
   - Validate file types and sizes
   - Scan for malware (recommended)
   - Implement rate limiting

2. **LaTeX Security:**
   - Disable shell-escape in LaTeX compilation
   - Run in sandboxed environment

3. **General Security:**
   - Use HTTPS in production
   - Implement CSRF protection
   - Regular security updates

## Monitoring and Logs

1. **Application logs:**
   ```bash
   docker-compose logs -f doc2latex-web
   ```

2. **Nginx logs:**
   ```bash
   docker-compose logs -f nginx
   ```

3. **Health check endpoint:**
   `GET /health` returns service status

## Support

For issues or questions:
1. Check application logs
2. Verify all dependencies are installed
3. Ensure LaTeX distribution is available
4. Contact system administrator