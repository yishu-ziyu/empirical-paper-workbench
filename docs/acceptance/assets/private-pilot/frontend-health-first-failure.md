# Frontend health first failure

Image built from 18adfdf. Nginx served `http://127.0.0.1:80/` inside the container, but its health probe `wget http://localhost:80/` failed twice with connection refused. The image resolves localhost to IPv6 while the configured Nginx listener is IPv4. Changed only the health probe to its actual 127.0.0.1 listener; do not mask the check or alter application readiness. Original container health inspect provided the two failures. Gateway correctly waited instead of starting early.
