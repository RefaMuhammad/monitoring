# 🟢 Uptime Monitor

Website availability checker dengan dukungan Facebook & Instagram detection.
Dibangun dengan Python + Streamlit + Playwright.

---

## Fitur

- Cek status URL setiap N menit (default 10 menit)
- Deteksi konten Facebook & Instagram yang dihapus via Playwright (headless Chromium)
- Deteksi redirect, keyword error, dan `<title>` halaman
- Log tersimpan ke file `uptime_log.txt` dengan format `datetime WIB : url : status`
- Download log langsung dari UI
- Timezone WIB (UTC+7)

---

## Requirement

| Software | Versi minimum |
|---|---|
| Python | 3.10+ |
| Ubuntu/Debian VPS | 20.04+ |

---

## Instalasi di VPS (Ubuntu/Debian)

### 1. Update sistem & install dependensi

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libxcomposite1 libxdamage1 libxrandr2 libgbm1 \
    libxkbcommon0 libpango-1.0-0 libasound2
```

### 2. Clone repo / upload file

**Jika pakai Git:**
```bash
git clone https://github.com/username/repo-kamu.git
cd repo-kamu
```

**Jika upload manual (scp):**
```bash
# Dari laptop kamu
scp monitor.py requirements.txt user@ip-vps:/home/user/monitoring/
ssh user@ip-vps
cd /home/user/monitoring/
```

### 3. Buat virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 5. Install Playwright & Chromium

```bash
playwright install chromium
playwright install-deps chromium
```

> `install-deps` wajib dijalankan di VPS untuk install semua library sistem yang dibutuhkan Chromium headless.

### 6. Test jalankan

```bash
streamlit run monitor.py --server.port 8501
```

Buka browser: `http://ip-vps-kamu:8501`

---

## Jalankan sebagai background service (systemd)

Supaya app tetap jalan meski terminal ditutup atau VPS restart.

### 1. Buat file service

```bash
sudo nano /etc/systemd/system/uptime-monitor.service
```

Isi dengan (sesuaikan path dan username):

```ini
[Unit]
Description=Uptime Monitor Streamlit
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/monitoring
ExecStart=/home/ubuntu/monitoring/venv/bin/streamlit run monitor.py --server.port 8501 --server.headless true
Restart=always
RestartSec=10
Environment="PATH=/home/ubuntu/monitoring/venv/bin"

[Install]
WantedBy=multi-user.target
```

### 2. Aktifkan service

```bash
sudo systemctl daemon-reload
sudo systemctl enable uptime-monitor
sudo systemctl start uptime-monitor
```

### 3. Cek status

```bash
sudo systemctl status uptime-monitor
```

### 4. Lihat log service

```bash
sudo journalctl -u uptime-monitor -f
```

---

## Akses dari internet (opsional — nginx reverse proxy)

Supaya bisa diakses via domain/subdomain tanpa port `:8501`.

### 1. Install nginx

```bash
sudo apt install -y nginx
```

### 2. Buat config nginx

```bash
sudo nano /etc/nginx/sites-available/uptime-monitor
```

```nginx
server {
    listen 80;
    server_name monitor.domain-kamu.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 3. Aktifkan config

```bash
sudo ln -s /etc/nginx/sites-available/uptime-monitor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. HTTPS dengan Certbot (opsional)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d monitor.domain-kamu.com
```

---

## Firewall (jika pakai ufw)

```bash
sudo ufw allow 8501    # jika akses langsung via port
sudo ufw allow 80      # jika pakai nginx
sudo ufw allow 443     # jika pakai HTTPS
sudo ufw enable
```

---

## Struktur file

```
monitoring/
├── monitor.py          # App utama
├── requirements.txt    # Python dependencies
├── README.md           # Panduan ini
└── uptime_log.txt      # Log hasil cek (auto-generated)
```

---

## Update app

```bash
cd /home/ubuntu/monitoring

# Jika pakai git
git pull

# Restart service
sudo systemctl restart uptime-monitor
```

---

## Troubleshooting

**Chromium tidak bisa jalan di VPS:**
```bash
playwright install-deps chromium
```

**Port 8501 tidak bisa diakses:**
```bash
sudo ufw allow 8501
# Pastikan juga security group VPS (AWS/GCP/dll) membuka port 8501
```

**App crash / tidak jalan:**
```bash
sudo journalctl -u uptime-monitor -n 50 --no-pager
```

**Cek manual tanpa systemd:**
```bash
source venv/bin/activate
streamlit run monitor.py --server.port 8501 --server.headless true
```
