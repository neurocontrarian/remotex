#!/bin/bash
# Verify or regenerate SHA256 hashes for Flatpak manifest dependencies.
#
# Usage:
#   bash build-aux/flatpak/gen-deps.sh          — verify all hashes
#   bash build-aux/flatpak/gen-deps.sh regen    — download + print corrected hashes
#
# The "regen" mode downloads every package listed in the manifest into /tmp/commandeck-flatpak-deps/
# and prints the sha256sum for each. Copy the output into io.github.neurocontrarian.commandeck.yml.
#
# Alternative (full dependency tree, recommended for Flathub submission):
#   pip3 install flatpak-pip-generator
#   python3 flatpak-pip-generator fabric tomli_w paramiko cairosvg \
#       --runtime org.gnome.Platform --runtime-version 47 \
#       -o build-aux/flatpak/python3-packages.json
#   # Then replace the inline Python modules in the manifest with:
#   # - build-aux/flatpak/python3-packages.json

set -e

WORKDIR=/tmp/commandeck-flatpak-deps
mkdir -p "$WORKDIR"

MODE="${1:-verify}"

declare -A PACKAGES=(
  # Pure Python — wheels
  ["tomli_w-1.2.0-py3-none-any.whl"]="https://files.pythonhosted.org/packages/c7/18/c86eb8e0202e32dd3df50d43d7ff9854f8e0603945ff398974c1d91ac1ef/tomli_w-1.2.0-py3-none-any.whl"
  ["invoke-3.0.3-py3-none-any.whl"]="https://files.pythonhosted.org/packages/5a/de/bbc12563bbf979618d17625a4e753ff7a078523e28d870d3626daa97261a/invoke-3.0.3-py3-none-any.whl"
  ["fabric-3.2.3-py3-none-any.whl"]="https://files.pythonhosted.org/packages/37/f9/f8497ef8b873a8bb2a750ee2a6c5f0fc22258e1acb6245fd237042a6c279/fabric-3.2.3-py3-none-any.whl"
  ["paramiko-4.0.0-py3-none-any.whl"]="https://files.pythonhosted.org/packages/a9/90/a744336f5af32c433bd09af7854599682a383b37cfd78f7de263de6ad6cb/paramiko-4.0.0-py3-none-any.whl"
  # C extensions — source tarballs
  ["pycparser-2.22.tar.gz"]="https://files.pythonhosted.org/packages/1d/b2/31537cf4b1ca988837256c910a668b553fceb8f069bedc4b1c826024b52c/pycparser-2.22.tar.gz"
  ["cffi-1.17.1.tar.gz"]="https://files.pythonhosted.org/packages/fc/97/c783634659c2920c3fc70419e3af40972dbaf758daa229a7d6ea6135c90d/cffi-1.17.1.tar.gz"
  ["cryptography-47.0.0.tar.gz"]="https://files.pythonhosted.org/packages/ef/b2/7ffa7fe8207a8c42147ffe70c3e360b228160c1d85dc3faff16aaa3244c0/cryptography-47.0.0.tar.gz"
  ["bcrypt-5.0.0.tar.gz"]="https://files.pythonhosted.org/packages/d4/36/3329e2518d70ad8e2e5819d5a4cac6bba05a47767ec416c7d020a965f408/bcrypt-5.0.0.tar.gz"
  ["pynacl-1.6.2.tar.gz"]="https://files.pythonhosted.org/packages/d9/9a/4019b524b03a13438637b11538c82781a5eda427394380381af8f04f467a/pynacl-1.6.2.tar.gz"
  ["cairocffi-1.7.1.tar.gz"]="https://files.pythonhosted.org/packages/70/c5/1a4dc131459e68a173cbdab5fad6b524f53f9c1ef7861b7698e998b837cc/cairocffi-1.7.1.tar.gz"
  ["cairosvg-2.9.0.tar.gz"]="https://files.pythonhosted.org/packages/38/07/e8412a13019b3f737972dea23a2c61ca42becafc16c9338f4ca7a0caa993/cairosvg-2.9.0.tar.gz"
  ["webencodings-0.5.1.tar.gz"]="https://files.pythonhosted.org/packages/0b/02/ae6ceac1baeda530866a85075641cec12989bd8d31af6d5ab4a3e8c92f47/webencodings-0.5.1.tar.gz"
  ["tinycss2-1.5.1.tar.gz"]="https://files.pythonhosted.org/packages/a3/ae/2ca4913e5c0f09781d75482874c3a95db9105462a92ddd303c7d285d3df2/tinycss2-1.5.1.tar.gz"
  ["cssselect2-0.9.0.tar.gz"]="https://files.pythonhosted.org/packages/e0/20/92eaa6b0aec7189fa4b75c890640e076e9e793095721db69c5c81142c2e1/cssselect2-0.9.0.tar.gz"
  ["defusedxml-0.7.1.tar.gz"]="https://files.pythonhosted.org/packages/0f/d5/c66da9b79e5bdb124974bfe172b4daf3c984ebd9c2a06e2b8a4dc7331c72/defusedxml-0.7.1.tar.gz"
  # wmctrl
  ["wmctrl-1.07.tar.gz"]="https://sourceforge.net/projects/wmctrl/files/wmctrl/1.07/wmctrl-1.07.tar.gz/download"
)

echo "=== Commandeck Flatpak dependency checker ==="
echo "Working dir: $WORKDIR"
echo ""

for filename in "${!PACKAGES[@]}"; do
  url="${PACKAGES[$filename]}"
  dest="$WORKDIR/$filename"

  if [ "$MODE" = "regen" ]; then
    if [ ! -f "$dest" ]; then
      echo "Downloading $filename..."
      wget -q -O "$dest" "$url" || curl -L -o "$dest" "$url"
    fi
    hash=$(sha256sum "$dest" | cut -d' ' -f1)
    echo "  $filename"
    echo "    sha256: $hash"
  else
    echo "URL: $url"
  fi
done

if [ "$MODE" = "regen" ]; then
  echo ""
  echo "Done. Paste the sha256 values above into io.github.neurocontrarian.commandeck.yml."
fi
