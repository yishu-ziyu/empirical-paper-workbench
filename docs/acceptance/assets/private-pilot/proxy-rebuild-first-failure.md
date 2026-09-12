# Proxy rebuild first failure

After the timestamp patch, backend/frontend containers were replaced while `compose up` reused the gateway. Nginx retained the previous frontend address; real HTTPS API requests returned 502 despite container health being green. No write replay was made. `ops.sh up` now explicitly recreates backend/runner/frontend/gateway together, as the rebuild operation already does. Read-only actual gateway `/api/auth/me` (with entry credentials, no app cookies) must return 401 before user tasks begin. Container health alone is insufficient.
