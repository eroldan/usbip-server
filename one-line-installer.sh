#!/usr/bin/env bash
set -euo pipefail

REPO="https://github.com/eroldan/test1.git"

echo "[INFO] Detecting distribution..."

if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    echo "[ERROR] Cannot detect OS"
    exit 1
fi

SUDO=sudo
if [ $(id -u) -eq 0 ]; then
    SUDO=""
fi


echo "[INFO] Distribution detected: $DISTRO"

install_ansible_deps_debian() {
    $SUDO apt-get update -y
    $SUDO apt-get install -y ansible git python3 python3-pip
}

install_ansible_deps_redhat() {
    # Enable EPEL only if Ansible not already in repos
    if ! yum list ansible >/dev/null 2>&1; then
        $SUDO yum install -y epel-release
    fi
    $SUDO yum install -y ansible git python3 python3-pip
}

install_ansible_deps_alpine() {
    $SUDO apk add --no-cache ansible git python3 py3-pip
}

# Choose correct installer based on distro

# Only support distributions listed in the playbook.yaml
case "$DISTRO" in
    ubuntu|debian|raspbian)
        install_ansible_deps_debian
        ;;
    fedora|rocky|centos)
        install_ansible_deps_redhat
        ;;
    *)
        echo "[ERROR] Unsupported distribution: $DISTRO"
        echo "Supported distributions: Debian, Ubuntu, Raspbian, Fedora, Rocky, Centos"
        exit 1
        ;;
esac


echo "[INFO] Installing or updating playbook..."

SKIP_GIT="${SKIP_GIT:=}"
if [ -n "$SKIP_GIT" ]; then
    echo "[INFO] Skipping git clone, using existing playbook directory."
else
    echo "[INFO] Cloning playbook repository..."
    INSTALL_DIR=$(mktemp --dry-run)
    git clone $REPO "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

pwd
HOST="${HOST:=localhost}"
echo "[INFO] Running Ansible playbook..."
set -x
ansible-playbook --inventory ${HOST}, --become --connection local playbook.yaml
