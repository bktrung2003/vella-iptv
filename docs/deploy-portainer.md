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
2. **Web editor**: dán nội dung [`platform/compose.portainer.ghcr.yml`](../platform/compose.portainer.ghcr.yml). File đã **nhúng sẵn** user/pass/SECRET_KEY/IP lab (`192.168.1.116`) — có thể **Deploy** luôn, không bắt buộc khai báo env trong Portainer.
3. **Environment variables** (tuỳ chọn): chỉ cần nếu bạn muốn override; ví dụ `IMAGE_TAG=v1.0.0` để rollback. Đổi IP/CORS/secret: sửa trực tiếp trong compose (hoặc tách lại env như bản cũ).
4. **Superuser đăng nhập dashboard lần đầu:** email `admin@vella-iptv.local`, mật khẩu = `FIRST_SUPERUSER_PASSWORD` trong file compose (đổi ngay sau khi vào được).
5. **Deploy the stack**

> ⚠️ Compose có secret **đọc được trên GitHub** (repo public). Chỉ dùng lab; production → đổi toàn bộ và không commit mật khẩu thật.

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
| `prestart` exit 1 | Xem log container `prestart` trên Portainer. Thường gặp: thiếu **`PROJECT_NAME`** trong env backend (Settings Pydantic lỗi ngay khi import), hoặc **`SENTRY_DSN=""`** (chuỗi rỗng không hợp lệ với kiểu URL), hoặc Alembic / không kết nối được Postgres. |
| **`db` unhealthy** | (1) Trong Portainer stack env phải có `POSTGRES_PASSWORD` (không để trống), nên có `POSTGRES_USER` / `POSTGRES_DB` hoặc để mặc định compose (`postgres` / `app`). (2) Xem log container `db`: lỗi quyền volume, mật khẩu, hoặc data cũ không khớp phiên bản Postgres. (3) Lần đầu init DB chậm — compose đã có `start_period: 90s`. (4) Đổi major image Postgres sau khi đã có volume → cần xóa volume `vella-iptv-db` (mất data) hoặc giữ đúng major cũ. |
| CORS chặn | Mở rộng `BACKEND_CORS_ORIGINS` đúng scheme/host/port |

---

## Liên quan

- Traefik + HTTPS công khai: [`platform/deployment.md`](../platform/deployment.md) + `compose.traefik.yml`
- Mẫu biến môi trường: [`platform/.env.example`](../platform/.env.example)
