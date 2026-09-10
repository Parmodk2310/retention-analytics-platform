#!/usr/bin/env bash
set -Eeuo pipefail

if test "$#" -ne 1; then
  echo "Usage: sudo $0 <administrator-ip>/32"
  exit 2
fi

if test "$(id -u)" -ne 0; then
  echo "ERROR: run this script with sudo"
  exit 1
fi

ADMIN_CIDR="$1"
DEPLOY_USER="${SUDO_USER:-ubuntu}"

if ! printf '%s\n' "$ADMIN_CIDR" |
    grep -Eq '^([0-9]{1,3}\.){3}[0-9]{1,3}/32$'; then
  echo "ERROR: administrator address must be an IPv4 /32 CIDR"
  exit 1
fi

if ! id "$DEPLOY_USER" >/dev/null 2>&1; then
  echo "ERROR: deployment user does not exist: $DEPLOY_USER"
  exit 1
fi

echo "===== UPDATE UBUNTU PACKAGES ====="

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get upgrade -y

apt-get install -y \
  ca-certificates \
  curl \
  git \
  gnupg \
  openssl \
  ufw \
  unattended-upgrades

echo "===== INSTALL DOCKER REPOSITORY ====="

install -m 0755 -d /etc/apt/keyrings

curl --fail --silent --show-error --location \
  https://download.docker.com/linux/ubuntu/gpg \
  --output /etc/apt/keyrings/docker.asc

chmod a+r /etc/apt/keyrings/docker.asc

. /etc/os-release

ARCHITECTURE="$(dpkg --print-architecture)"

printf '%s\n' \
  "deb [arch=${ARCHITECTURE} signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" \
  >/etc/apt/sources.list.d/docker.list

apt-get update

apt-get install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

systemctl enable --now docker
usermod -aG docker "$DEPLOY_USER"

echo "===== HARDEN SSH ====="

install -m 0755 -d /etc/ssh/sshd_config.d

cat >/etc/ssh/sshd_config.d/99-retention-hardening.conf <<'SSH'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
PubkeyAuthentication yes
X11Forwarding no
MaxAuthTries 3
SSH

sshd -t
systemctl restart ssh

echo "===== CONFIGURE FIREWALL ====="

ufw --force reset
ufw default deny incoming
ufw default allow outgoing

ufw allow from "$ADMIN_CIDR" to any port 22 proto tcp \
  comment "Restricted administrator SSH"

ufw allow 80/tcp comment "Public HTTP"
ufw allow 443/tcp comment "Public HTTPS"
ufw allow 443/udp comment "Public HTTP3"

ufw --force enable

echo "===== ENABLE AUTOMATIC SECURITY UPDATES ====="

dpkg-reconfigure -f noninteractive unattended-upgrades

echo "===== VERIFY HOST ====="

docker --version
docker compose version
ufw status verbose
sshd -t

echo
echo "PASS: OCI host bootstrap completed"
echo "IMPORTANT: sign out and reconnect for Docker group access."
