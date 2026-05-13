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
   - Value: URL mà trình duyệt gọi được tới backend — **cổng publish mặc định trên host là 7000**, ví dụ `http://192.168.1.116:7000` (khớp `BACKEND_PUBLISH_PORT` trong env stack)

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
2. **Web editor**: dán [`platform/compose.portainer.ghcr.yml`](../platform/compose.portainer.ghcr.yml) (file trên Git **không** chứa mật khẩu — an toàn khi repo public).
3. **Environment variables**: dán nội dung từ [`platform/compose.portainer.ghcr.env.example`](../platform/compose.portainer.ghcr.env.example), điền `SECRET_KEY`, `POSTGRES_PASSWORD`, `FIRST_SUPERUSER`, `FIRST_SUPERUSER_PASSWORD`, `SERVER_IP`, v.v. (có thể lưu bản riêng trên máy `compose.portainer.ghcr.env` — file này nằm trong `.gitignore`.)
4. **Deploy the stack**

Truy cập (thay IP cho đúng; backend **host** mặc định cổng **7000**):

- API docs: `http://192.168.1.116:7000/docs`
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
| `prestart` exit 1 | Xem log `prestart`. Thường gặp: thiếu **`SECRET_KEY`** / **`POSTGRES_PASSWORD`** trong env stack, hoặc Alembic / không kết nối Postgres. `PROJECT_NAME` có default trong compose; có thể override bằng env. |
| **`db` unhealthy** | (1) `POSTGRES_PASSWORD` bắt buộc trong env stack. (2) `POSTGRES_USER` / `POSTGRES_DB` mặc định `vella` / `vella_iptv` nếu không set. (3) Log container `db` — volume / version Postgres. (4) `start_period: 90s` cho ổ chậm. |
| CORS chặn | Mở rộng `BACKEND_CORS_ORIGINS` đúng scheme/host/port |

---

## Liên quan

- Traefik + HTTPS công khai: [`platform/deployment.md`](../platform/deployment.md) + `compose.traefik.yml`
- Portainer env mẫu: [`platform/compose.portainer.ghcr.env.example`](../platform/compose.portainer.ghcr.env.example)
- Dev local: [`platform/.env.example`](../platform/.env.example)
