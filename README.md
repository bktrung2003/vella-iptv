# Vella IPTV

Control plane (FastAPI + dashboard) và tài nguyên UI/research cho IPTV khách sạn.

- **`platform/`** — [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) (backend, React, Docker Compose).
- **`scripts/`** — batch Windows: `platform-start.bat` / `platform-stop.bat` (cần Docker local).
- **`ui/`** — prototype giao diện TV.

## GitHub

<https://github.com/bktrung2003/vella-iptv>

## Chỉnh cho khớp — từng luồng

| Bạn đang làm gì | Sửa **ở đâu** | Ghi chú |
|-----------------|---------------|---------|
| **Portainer** | Đọc **[`platform/PORTAINER-BAN-SUA-GI.txt`](platform/PORTAINER-BAN-SUA-GI.txt)** (chỉ rõ dán file nào, dòng nào bắt buộc sửa). Compose: [`compose.portainer.ghcr.yml`](platform/compose.portainer.ghcr.yml). Env mẫu: [`compose.portainer.ghcr.env.example`](platform/compose.portainer.ghcr.env.example). | |
| **GitHub Actions** (build frontend) | **Variables** → `VITE_API_URL` | Phải trùng URL API ngoài (mặc định stack dùng cổng host **7000**): `http://<IP>:7000` → **Re-run workflow** → Portainer **Pull and redeploy**. |
| **Máy dev có Docker** | [`platform/.env.example`](platform/.env.example) → `platform/.env` | Không dùng cho Portainer. |

**Đổi IP server (ví dụ `192.168.1.50`):** trong Portainer đặt `SERVER_IP=192.168.1.50`, chỉnh `VITE_API_URL=http://192.168.1.50:7000` trên GitHub → build lại → redeploy.

**Đổi cổng backend trên host:** `BACKEND_PUBLISH_PORT` (mặc định **7000**; container vẫn listen `8000` bên trong).

## CI → GHCR → Portainer (tóm tắt)

1. Push `main` → [`.github/workflows/build-push-ghcr.yml`](.github/workflows/build-push-ghcr.yml).
2. `VITE_API_URL` = `http://<IP>:<BACKEND_PUBLISH_PORT>` (thường port **7000**).
3. Portainer: compose + env → Deploy / **Pull and redeploy**.

Chi tiết: [docs/deploy-portainer.md](docs/deploy-portainer.md).

### Traefik + HTTPS (tùy chọn)

[platform/deployment.md](platform/deployment.md) và `compose.traefik.yml`.
