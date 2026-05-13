# Vella IPTV

Control plane (FastAPI + dashboard) và tài nguyên UI/research cho IPTV khách sạn.

- **`platform/`** — [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) (backend, frontend, Docker Compose).
- **`scripts/`** — batch Windows: `platform-start.bat` / `platform-stop.bat` (cần Docker local).
- **`ui/`** — prototype giao diện TV.

## GitHub

<https://github.com/bktrung2003/vella-iptv>

## Chỉnh cho khớp — chỉ **một chỗ** tùy cách bạn chạy

Đừng trộn `.env` với Portainer: **mỗi luồng có file riêng**, không tự “khớp” với nhau.

| Bạn đang làm gì | Sửa **ở đâu** | Việc cần nhớ |
|-----------------|---------------|--------------|
| **Portainer** (dán stack, kéo image GHCR) | Chỉ [`platform/compose.portainer.ghcr.yml`](platform/compose.portainer.ghcr.yml) | IP (`DOMAIN`, `FRONTEND_HOST`, `BACKEND_CORS_ORIGINS`), user/pass DB, superuser, `SECRET_KEY` đều nằm trong file này. **Không** cần `platform/.env` cho stack đó. |
| **GitHub Actions** (build image frontend) | Repo → **Settings → Secrets and variables → Actions → Variables** → `VITE_API_URL` | Phải **cùng host:port** với API thật (vd máy bạn là `http://192.168.1.116:8000`). Đổi IP trong compose → **đổi luôn** biến này → **Re-run workflow** → Portainer **Pull and redeploy**. |
| **Máy dev có Docker** (`docker compose` trong `platform/`) | `platform/.env` (+ tuỳ chọn `platform/frontend/.env`) | Copy từ [`platform/.env.example`](platform/.env.example). Không dùng cho stack Portainer hiện tại. |

**Thứ tự cho khớp IP (ví dụ đổi sang `192.168.1.50`):**

1. Sửa IP trong `compose.portainer.ghcr.yml` (khối `x-vella-backend-env`: `DOMAIN`, `FRONTEND_HOST`, `BACKEND_CORS_ORIGINS`).
2. Trên GitHub đặt `VITE_API_URL=http://192.168.1.50:8000` → Actions → chạy lại **Build and Push GHCR**.
3. Portainer → stack → **Pull and redeploy**.

## CI → GHCR → Portainer (tóm tắt)

1. Push `main` → workflow [`.github/workflows/build-push-ghcr.yml`](.github/workflows/build-push-ghcr.yml) build & push image.
2. `VITE_API_URL` trên GitHub (bước trên bảng).
3. Portainer: dán [`platform/compose.portainer.ghcr.yml`](platform/compose.portainer.ghcr.yml) → Deploy / **Pull and redeploy**.

Chi tiết: [docs/deploy-portainer.md](docs/deploy-portainer.md).

### Traefik + HTTPS (tùy chọn, production public)

Tạo mạng `traefik-public`, xem [platform/deployment.md](platform/deployment.md) và `compose.traefik.yml`.
