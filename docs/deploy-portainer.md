# Playbook: Vella IPTV — Deploy qua GHCR + Portainer

Áp dụng cùng **tư duy luồng** như playbook ITBM (`D:\SACAI\.claude\knowledge\03-Playbooks\itbm-deploy-workflow.md`): CI build image trên GitHub → push **GHCR** → Portainer **pull & redeploy** (thủ công).

---

## Stack overview

| Thành phần | Chi tiết |
|------------|----------|
| Repo | https://github.com/bktrung2003/vella-iptv |
| Branch chính | `main` |
| CI | [`.github/workflows/build-push-ghcr.yml`](../.github/workflows/build-push-ghcr.yml) — chạy khi push `main` hoặc tag `v*` |
| Image backend | `ghcr.io/bktrung2003/vella-iptv-backend:latest` |
| Image frontend | `ghcr.io/bktrung2003/vella-iptv-frontend:latest` |
| Compose Portainer | [`platform/compose.portainer.ghcr.yml`](../platform/compose.portainer.ghcr.yml) |
| CD | Thủ công — Portainer **Pull and redeploy** sau khi Actions xanh |

**Lưu ý:** Workflow GitHub nằm ở **root** repo (`.github/workflows/`). Thư mục `platform/.github/workflows/` từ template **không** được GitHub chạy tự động.

---

## Hiểu nhanh project (từ các file .md)

- **Root [`README.md`](../README.md)** — cấu trúc monorepo: `platform/` (FastAPI + React + Compose), `ui/` prototype TV, `scripts/` Windows.
- **[`platform/README.md`](../platform/README.md)** — template full-stack (SQLModel, Postgres, Traefik production).
- **[`platform/deployment.md`](../platform/deployment.md)** — Traefik công khai, DNS wildcard, Let’s Encrypt; phù hợp **public cloud**.
- **[`platform/development.md`](../platform/development.md)** — `docker compose watch` local, port 8000 / 5173.
- **Portainer LAN (192.168.1.x):** dùng [`compose.portainer.ghcr.yml`](../platform/compose.portainer.ghcr.yml) — **publish port** trực tiếp, không bắt buộc Traefik.

---

## Setup lần đầu

### 1 — GitHub: biến `VITE_API_URL` (Repository variables)

Frontend build **embed** URL API vào bundle.

1. Repo → **Settings** → **Secrets and variables** → **Actions** → tab **Variables**
2. **New repository variable**
   - Name: `VITE_API_URL`
   - Value: URL mà trình duyệt gọi được tới backend, ví dụ `http://192.168.1.116:8000` (cùng host/IP với máy chạy Docker)

Sau đó push lại `main` (hoặc chạy workflow **workflow_dispatch**) để image frontend được build đúng API URL.

### 2 — GitHub Container Registry: quyền pull

- Nếu package **private:** tạo PAT (scope **`read:packages`**) như playbook ITBM.
- Portainer → **Registries** → thêm **Custom** `ghcr.io`, user `bktrung2003`, password = PAT.

Hoặc vào package trên GitHub → **Package settings** → **Change visibility** → **Public** (đơn giản cho lab).

### 3 — Push code để CI build

```bash
git push origin main
```

Vào **Actions** → workflow **Build and Push GHCR** → chờ ✅.

Packages:

- https://github.com/bktrung2003?tab=packages (tìm `vella-iptv-backend`, `vella-iptv-frontend`)

### 4 — Tạo stack trên Portainer

1. **Stacks** → **Add stack** → tên ví dụ `vella-iptv`
2. **Web editor**: dán nội dung file [`platform/compose.portainer.ghcr.yml`](../platform/compose.portainer.ghcr.yml) (copy từ repo sau khi pull).
3. **Environment variables** (bổ sung / chỉnh — không commit secret lên Git):

| Biến | Gợi ý |
|------|--------|
| `IMAGE_TAG` | `latest` (bình thường); rollback: `v1.0.1` |
| `DOMAIN` | Hostname hoặc IP dùng trong CORS/email, ví dụ `192.168.1.116` |
| `ENVIRONMENT` | `production` |
| `PROJECT_NAME` | `Vella IPTV` |
| `STACK_NAME` | `vella-iptv` |
| `SECRET_KEY` | Sinh: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `POSTGRES_PASSWORD` | Mật khẩu mạnh |
| `POSTGRES_USER` | `postgres` |
| `POSTGRES_DB` | `app` |
| `FIRST_SUPERUSER` | Email admin |
| `FIRST_SUPERUSER_PASSWORD` | Mật khẩu mạnh |
| `FRONTEND_HOST` | `http://192.168.1.116:5173` (khớp port publish) |
| `BACKEND_CORS_ORIGINS` | Gồm `http://192.168.1.116:5173` và các origin TV kiosk nếu có |
| `BACKEND_PUBLISH_PORT` | `8000` |
| `FRONTEND_PUBLISH_PORT` | `5173` |
| `ADMINER_PUBLISH_PORT` | `8080` |
| `IPTV_GATEWAY_HLS_BASE_URL` | (tuỳ chọn) URL gateway HLS nội bộ |

4. **Deploy the stack**

Truy cập thử:

- API docs: `http://192.168.1.116:8000/docs`
- Dashboard: `http://192.168.1.116:5173`
- Adminer: `http://192.168.1.116:8080`

---

## Quy trình cập nhật (giống ITBM)

1. Sửa code local → commit → `git push origin main`
2. Chờ **Build and Push GHCR** ✅
3. Portainer → stack `vella-iptv` → **Pull and redeploy**
4. Hard refresh browser: `Ctrl+Shift+R`

---

## Versioning & rollback

```bash
git tag -a v1.0.0 -m "v1.0.0"
git push origin v1.0.0
```

Actions sẽ push image tag `v1.0.0` (và `latest` trên main theo cấu hình metadata).

**Quy tắc:** Stack thường để `IMAGE_TAG=latest`. Khi rollback: đổi `IMAGE_TAG=v1.0.0` → **Update the stack** → verify → đổi lại `latest` + Pull and redeploy.

---

## Troubleshooting

| Triệu chứng | Hướng xử lý |
|-------------|-------------|
| Actions không chạy | Kiểm tra file tại **root** `.github/workflows/build-push-ghcr.yml`, branch `main` |
| Portainer pull 401 | Đăng ký registry GHCR + PAT `read:packages`, hoặc để package public |
| Frontend gọi sai API | Chỉnh **variable** `VITE_API_URL` trên GitHub → chạy lại workflow → redeploy |
| `prestart` exit lỗi | Xem log container `prestart` (Alembic / DB connection) |
| CORS chặn | Mở rộng `BACKEND_CORS_ORIGINS` đúng scheme/host/port |

---

## Liên quan

- Traefik + HTTPS công khai: [`platform/deployment.md`](../platform/deployment.md) + `compose.traefik.yml`
- Mẫu biến môi trường: [`platform/.env.example`](../platform/.env.example)
