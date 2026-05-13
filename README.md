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

## Portainer (Ubuntu, ví dụ 192.168.1.116)

1. Trên host: tạo mạng Traefik nếu dùng stack production có `traefik-public` external:

   `docker network create traefik-public`

2. Trong Portainer: **Stacks → Add stack → Repository** (hoặc dán compose), trỏ repo này và file compose phù hợp (xem `platform/deployment.md`).

3. Thêm biến môi trường trong Portainer (hoặc file env) khớp với `.env.example`; đổi `DOMAIN`, `SECRET_KEY`, mật khẩu DB, `FRONTEND_HOST` / `BACKEND_CORS_ORIGINS` theo URL thật (IP hoặc DNS nội bộ).

4. Build: dùng **GitHub Actions** build & push image lên registry, rồi trong compose thay `build:` bằng `image:` — hoặc để Portainer build từ Git (Webhooks / polling).

Chi tiết HTTPS/Traefik: [platform/deployment.md](platform/deployment.md).
