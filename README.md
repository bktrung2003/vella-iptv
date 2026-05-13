# Vella IPTV

Control plane (FastAPI + dashboard) và tài nguyên UI/research cho IPTV khách sạn.

- **`platform/`** — [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) (backend, frontend, Docker Compose).
- **`scripts/`** — batch Windows: `platform-start.bat` / `platform-stop.bat` (cần Docker local).
- **`ui/`** — prototype giao diện TV.

## GitHub

<https://github.com/bktrung2003/vella-iptv>

## Cấu hình môi trường

1. `copy platform\.env.example platform\.env` (và chỉnh giá trị).
2. `copy platform\frontend\.env.example platform\frontend\.env` nếu build frontend local.
3. Không commit `platform/.env` — đã nằm trong `.gitignore`.

## CI → GHCR → Portainer

1. Push `main` (hoặc tag `v*`) để chạy workflow **Build and Push GHCR** (file [`.github/workflows/build-push-ghcr.yml`](.github/workflows/build-push-ghcr.yml)).
2. Trên GitHub repo → **Settings → Variables**: đặt `VITE_API_URL` (ví dụ `http://192.168.1.116:8000`) rồi chạy lại workflow để frontend embed đúng API.
3. Portainer: dán compose [`platform/compose.portainer.ghcr.yml`](platform/compose.portainer.ghcr.yml), thêm biến môi trường, **Pull and redeploy** sau mỗi build.

**Playbook đầy đủ:** [docs/deploy-portainer.md](docs/deploy-portainer.md) (cùng luồng với playbook ITBM trong `.claude/knowledge`).

### Traefik + HTTPS (tùy chọn, production public)

Tạo mạng `traefik-public`, xem [platform/deployment.md](platform/deployment.md) và `compose.traefik.yml`.
